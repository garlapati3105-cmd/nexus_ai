import sys

def main():
    src = r"c:\Users\hp\Downloads\nexus_ai\apps\api\test_results.txt"
    dst = r"c:\Users\hp\Downloads\nexus_ai\apps\api\test_results_utf8.txt"
    try:
        with open(src, "r", encoding="utf-16") as f:
            content = f.read()
        with open(dst, "w", encoding="utf-8") as f:
            f.write(content)
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
