import sys
import os
import platform
import asyncio

print("=== Environment Test ===")
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Current Directory: {os.getcwd()}")
print(f"Python Executable: {sys.executable}")
print("\nTesting asyncio...")

async def test_async():
    print("✅ Asyncio is working!")
    return "Success"

# Run the async test
result = asyncio.run(test_async())
print(f"Async test result: {result}")

print("\nTesting complete!")
