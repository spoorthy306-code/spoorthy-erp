#!/bin/bash
echo "Testing Spoorthy ERP API with Authentication"
echo "============================================="

# Login to get token
echo -e "\n1. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))")

if [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Got token: ${TOKEN:0:50}..."

# Test dashboard
echo -e "\n2. Testing dashboard summary..."
curl -s -X GET http://localhost:8000/api/v1/accounts/dashboard/summary \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool

# Test user profile
echo -e "\n3. Testing user profile..."
curl -s -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool

# Test account groups
echo -e "\n4. Testing account groups..."
curl -s -X GET http://localhost:8000/api/v1/accounts/groups \
  -H "Authorization: Bearer $TOKEN" \
  | python -m json.tool

echo -e "\n✅ Tests completed!"
