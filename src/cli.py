import sys
import os
import argparse
from dotenv import load_dotenv
from src.extractors.paragraphs import split_into_paragraphs
from src.agents.tooling import DbInsertTool
from src.agents.company_agent import CompanyAgent

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Extract companies from an essay file and insert into DB")
    parser.add_argument("essay_file", help="Path to the essay text file")
    args = parser.parse_args()

    with open(args.essay_file, "r", encoding="utf-8") as f:
        essay = f.read()

    paragraphs = split_into_paragraphs(essay)
    agent = CompanyAgent(DbInsertTool())
    for p in paragraphs:
        result = agent.process_paragraph(p)
        agent.insert_records(result)
    print(f"Processed {len(paragraphs)} paragraphs.")

if __name__ == "__main__":
    main()
