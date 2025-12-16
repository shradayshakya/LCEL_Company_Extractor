from typing import List
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_core.prompts import PromptTemplate
import os
import boto3
from langchain_aws import ChatBedrock
from pydantic import ValidationError
from .tooling import DbInsertTool
from ..extractors.company_schema import CompanyRecord, ExtractionResult
from ..extractors.normalize import normalize_date

LLM = ChatBedrock(
    model=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1"),
)

company_prompt = PromptTemplate(
    input_variables=["paragraph"],
    template=(
        """
        Extract structured company details from the paragraph.
        Return a JSON list of objects with keys: company_name, founded_in (date string), founded_by (list of names).
        Paragraph:\n{paragraph}
        """
    ),
)

parse_json = RunnableLambda(lambda x: x)


def _make_bedrock_llm():
    bedrock_client = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    )
    model_id = os.getenv("BEDROCK_MODEL_ID") or "amazon.nova-lite-v1:0"
    temperature = float(os.getenv("BEDROCK_TEMPERATURE", "0.2"))
    return ChatBedrock(client=bedrock_client, model_id=model_id, temperature=temperature)


def build_extractor():
    llm = _make_bedrock_llm()
    chain = company_prompt | llm | RunnableLambda(lambda x: x.content)
    return chain


def _clean_json_text(text: str) -> str:
    """
    Make the LLM output parseable JSON by removing Markdown code fences
    and isolating the JSON substring if extra prose is present.
    """
    t = text.strip()
    # Remove Markdown code fences like ```json ... ``` or ``` ... ```
    import re
    m = re.search(r"```(?:json|JSON)?\s*(.*?)```", t, flags=re.DOTALL)
    if m:
        t = m.group(1).strip()

    # If there is extra prose around JSON, isolate the primary JSON block
    starts = [i for i in [t.find("["), t.find("{")] if i != -1]
    if starts:
        start = min(starts)
        if t[start] == "[":
            end = t.rfind("]")
        else:
            end = t.rfind("}")
        if end != -1 and end >= start:
            t = t[start : end + 1].strip()
    return t


def to_records(json_text: str) -> ExtractionResult:
    import json

    try:
        items = json.loads(_clean_json_text(json_text))
        records: List[CompanyRecord] = []
        for it in items:
            d = normalize_date(it.get("founded_in"))
            if d is None:
                continue
            try:
                rec = CompanyRecord(
                    company_name=it.get("company_name"),
                    founded_in=d,
                    founded_by=list(it.get("founded_by", [])),
                )
                records.append(rec)
            except ValidationError as ve:
                pass
        return ExtractionResult(records=records)
    except Exception as e:
        return ExtractionResult(records=[], errors=[str(e)])


class CompanyAgent:
    def __init__(self, db_tool: DbInsertTool):
        self.db_tool = db_tool
        self.extractor = build_extractor()

    def process_paragraph(self, paragraph: str) -> ExtractionResult:
        json_text = self.extractor.invoke({"paragraph": paragraph})
        return to_records(json_text)

    def insert_records(self, result: ExtractionResult):
        for r in result.records:
            self.db_tool.run(
                company_name=r.company_name,
                founded_in=r.founded_in,
                founded_by=r.founded_by,
            )
