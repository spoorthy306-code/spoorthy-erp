#!/bin/bash
echo "Testing Spoorthy ERP API"
echo "========================"

echo -e "\n1. Testing root endpoint:"
curl -s http://localhost:8000/ | python -m json.tool

echo -e "\n2. Testing health check:"
curl -s http://localhost:8000/health | python -m json.tool

echo -e "\n3. Testing test endpoint:"
curl -s http://localhost:8000/api/v1/test | python -m json.tool

echo -e "\n4. Testing accounts dashboard (may require auth):"
curl -s http://localhost:8000/api/v1/accounts/dashboard/summary | python -m json.tool

echo -e "\n✅ Tests completed!"
