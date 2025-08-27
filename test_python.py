import sys
import platform
import asyncio

print("=== Python Environment Test ===")
print(f"Python Version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Python Executable: {sys.executable}")
print("\nTesting asyncio...")

async def test():
    print("✅ Asyncio is working!")
    return "Success"

# Run the test
result = asyncio.run(test())
print(f"Test result: {result}")

print("\n✅ Environment test completed!")
