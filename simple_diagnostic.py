"""
Simple diagnostic script to test basic Python and network functionality.
"""
import sys
import socket

def check_python():
    print("=== Python Environment ===")
    print(f"Python Version: {sys.version}")
    print(f"Executable: {sys.executable}")
    print(f"Platform: {sys.platform}")
    print(f"Encoding: {sys.getdefaultencoding()}")
    print()

def check_network(host="localhost", port=1234):
    print("=== Network Connection Test ===")
    print(f"Testing connection to {host}:{port}...")
    
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # 5 second timeout
        
        # Attempt to connect
        result = sock.connect_ex((host, port))
        
        if result == 0:
            print("✅ Successfully connected to the server!")
            
            # Try to read the server response
            try:
                response = sock.recv(1024)
                print(f"Server response: {response.decode('utf-8', errors='ignore')}")
            except socket.timeout:
                print("ℹ️ Connected but no data received (timeout)")
            except Exception as e:
                print(f"⚠️ Could not read server response: {e}")
        else:
            print(f"❌ Could not connect to {host}:{port}")
            print("Error code:", result)
            print("\nPlease ensure:")
            print("1. LM Studio is running")
            print("2. The local server is enabled in LM Studio")
            print("3. The server is configured to listen on the correct port")
            
    except socket.gaierror:
        print("❌ Hostname could not be resolved")
    except socket.error as e:
        print(f"❌ Socket error: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        sock.close()
    print()

def main():
    print("JARVIS Diagnostic Tool")
    print("=====================")
    
    check_python()
    check_network()
    
    print("\nDiagnostic complete.")
    print("If you're having issues, please check:")
    print("1. Is LM Studio running?")
    print("2. Is the local server enabled in LM Studio?")
    print("3. Is the correct port (1234) being used?")
    print("4. Is your firewall blocking the connection?")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
