#!/usr/bin/env python3
"""
Test script for GPT integration in Rasa chatbot.
This script tests the OpenAI integration without requiring a full Rasa setup.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_env_setup():
    """Test if environment variables are properly set."""
    print("🧪 Testing environment setup...")
    
    # Check for both possible API key names
    deepseek_key = os.getenv('DEEPSEEK_API_KEY') or os.getenv('OPENROUTER_API_KEY')
    if deepseek_key:
        # Mask the key for security
        masked_key = f"{deepseek_key[:8]}{'*' * (len(deepseek_key) - 12)}{deepseek_key[-4:]}" if len(deepseek_key) > 12 else "***"
        key_type = "OPENROUTER_API_KEY" if os.getenv('OPENROUTER_API_KEY') else "DEEPSEEK_API_KEY"
        print(f"✅ {key_type} found: {masked_key}")
        return True
    else:
        print("❌ OPENROUTER_API_KEY or DEEPSEEK_API_KEY not found in environment variables")
        print("   Please add your OpenRouter API key to the .env file:")
        print("   OPENROUTER_API_KEY=your_actual_api_key_here")
        return False

def test_openai_import():
    """Test if OpenAI library can be imported (used for DeepSeek compatibility)."""
    print("\n🧪 Testing OpenAI library import (for DeepSeek compatibility)...")
    
    try:
        import openai
        print("✅ OpenAI library imported successfully")
        print(f"   OpenAI version: {openai.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import OpenAI library: {e}")
        print("   Please install the OpenAI library:")
        print("   pip install openai>=1.0.0")
        return False

def test_deepseek_connection():
    """Test if we can connect to DeepSeek via OpenRouter API."""
    print("\n🧪 Testing DeepSeek via OpenRouter API connection...")
    
    try:
        import openai
        
        api_key = os.getenv('DEEPSEEK_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528-qwen3-8b:free",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond with exactly 'Connection test successful'."},
                {"role": "user", "content": "Test connection"}
            ],
            max_tokens=10,
            timeout=10,
            extra_headers={
                "HTTP-Referer": "https://localhost:5005",
                "X-Title": "Rasa License Chatbot Test",
            }
        )
        
        if response.choices and len(response.choices) > 0:
            result = response.choices[0].message.content
            if result is not None:
                result = result.strip()
                print(f"✅ DeepSeek via OpenRouter API connection successful! Response: '{result}'")
                return True
            else:
                print("⚠️  API responded but with empty content - this may be normal for the free model")
                return True  # Consider this a success since we got a valid response structure
        else:
            print("❌ No response from DeepSeek via OpenRouter API")
            return False
            
    except Exception as e:
        print(f"❌ DeepSeek via OpenRouter API connection failed: {e}")
        if "api_key" in str(e).lower():
            print("   Check your API key in the .env file")
        elif "quota" in str(e).lower() or "credit" in str(e).lower():
            print("   You may have exceeded your API quota or need credits")
        elif "timeout" in str(e).lower():
            print("   Connection timeout - check your internet connection")
        return False

def test_rasa_imports():
    """Test if Rasa-related imports work."""
    print("\n🧪 Testing Rasa imports...")
    
    try:
        from rasa_sdk import Action, Tracker
        from rasa_sdk.executor import CollectingDispatcher
        print("✅ Rasa SDK imports successful")
        return True
    except ImportError as e:
        print(f"❌ Failed to import Rasa SDK: {e}")
        print("   Please install Rasa SDK:")
        print("   pip install rasa>=3.6.15")
        return False

def test_gpt_action_import():
    """Test if the DeepSeek actions can be imported."""
    print("\n🧪 Testing DeepSeek action imports...")
    
    try:
        # Add the actions directory to the path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'actions'))
        
        from actions import ActionGPTFallback, ActionGPTQuery
        print("✅ DeepSeek actions imported successfully")
        
        # Test instantiation
        gpt_fallback = ActionGPTFallback()
        gpt_query = ActionGPTQuery()
        
        print(f"   ActionGPTFallback name: {gpt_fallback.name()}")
        print(f"   ActionGPTQuery name: {gpt_query.name()}")
        
        return True
    except ImportError as e:
        print(f"❌ Failed to import DeepSeek actions: {e}")
        return False
    except Exception as e:
        print(f"⚠️  DeepSeek actions imported but failed to instantiate: {e}")
        print("   This might be due to missing DeepSeek API key")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting DeepSeek via OpenRouter Integration Tests for Rasa Chatbot\n")
    
    tests = [
        test_env_setup,
        test_openai_import,
        test_rasa_imports,
        test_gpt_action_import,
        test_deepseek_connection,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DeepSeek via OpenRouter integration is ready to use.")
        print("\n📝 Next steps:")
        print("1. OpenRouter API key is already configured in the .env file")
        print("2. Train the Rasa model: rasa train")
        print("3. Start the action server: rasa run actions")
        print("4. Start the Rasa server: rasa run")
        print("5. Test the chatbot with DeepSeek via OpenRouter integration")
    else:
        print("❌ Some tests failed. Please fix the issues above before using DeepSeek via OpenRouter integration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
