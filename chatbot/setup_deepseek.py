#!/usr/bin/env python3
"""
Setup script for DeepSeek integration.
This script helps users set up their DeepSeek API key and validate the integration.
"""

import os
import sys

def setup_api_key():
    """Guide user through API key setup."""
    print("🔧 Setting up DeepSeek API Key")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"❌ {env_file} file not found!")
        return False
    
    # Read current .env file
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Check if API key is already set
    if 'DEEPSEEK_API_KEY=' in content and 'your_deepseek_api_key_here' not in content:
        print("✅ DeepSeek API key appears to already be configured in .env file")
        return True
    
    print("\n📝 To complete the DeepSeek integration setup:")
    print("1. Get your DeepSeek API key from: https://platform.deepseek.com")
    print("2. Open the .env file in a text editor")
    print("3. Replace 'your_deepseek_api_key_here' with your actual API key")
    print("4. Save the file")
    print("\nExample:")
    print("DEEPSEEK_API_KEY=sk-1234567890abcdef...")
    
    print("\n⚠️  Important Notes:")
    print("- Keep your API key secure and never share it")
    print("- The .env file is already in .gitignore for security")
    print("- You'll be charged for DeepSeek API usage (typically much cheaper than OpenAI)")
    
    return False

def main():
    """Main setup function."""
    print("🚀 DeepSeek Integration Setup")
    print("=" * 30)
    
    # Check if we're in the right directory
    if not os.path.exists("actions/actions.py"):
        print("❌ Please run this script from the chatbot root directory")
        return False
    
    # Setup API key
    api_key_ready = setup_api_key()
    
    print("\n🧪 Testing Setup...")
    
    # Run the test script
    try:
        import subprocess
        result = subprocess.run([sys.executable, "test_deepseek_integration.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ All tests passed! DeepSeek integration is ready to use.")
        else:
            print("⚠️  Some tests failed. Check the output above.")
            print("\nTest output:")
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
    
    print("\n📋 Next Steps:")
    if not api_key_ready:
        print("1. ⚠️  Set up your DeepSeek API key (see instructions above)")
        print("2. Run this script again to verify setup")
    else:
        print("1. ✅ API key is configured")
    
    print("2. Train the model: rasa train")
    print("3. Start action server: rasa run actions")
    print("4. Start chat server: rasa run")
    print("5. Test the chatbot!")
    
    print("\n💡 Usage Examples:")
    print('- "Check my license status" (original functionality)')
    print('- "Ask AI about safe driving tips" (new DeepSeek feature)')
    print('- "What\'s the weather?" (DeepSeek handles general questions)')
    print('- Random text → DeepSeek provides helpful fallback')
    
    return True

if __name__ == "__main__":
    main()
