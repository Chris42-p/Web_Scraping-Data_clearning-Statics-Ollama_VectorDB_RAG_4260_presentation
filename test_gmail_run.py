from Modules.engine_injesting.injest_engine import Injest_Engine

def main():
    engine = Injest_Engine(
        input_files_path="__injest",
        output_files_path="__output",
        credentials_path="credentials.json",
        token_path="token.json",
        ingest_dir="__ingest"
    )
    result = engine.ingest_gmail(max_emails=3)
    print("Fetched emails:")
    for idx, item in enumerate(result, start=1):
        print(f"\nEmail {idx}:")
        print("Saved to:", item["saved_to"])
        print("Parsed title:", item["parsed_email"]["title"])

if __name__ == "__main__":
    main()
