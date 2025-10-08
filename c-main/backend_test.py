#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class StyleSphereAPITester:
    def __init__(self, base_url="https://style-sphere-3.preview.emergentagent.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details
        })

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/")
            success = response.status_code == 200 and "StyleSphere Fashion API" in response.text
            self.log_test("API Root Endpoint", success, 
                         f"Status: {response.status_code}, Response: {response.text[:100]}")
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, str(e))
            return False

    def test_get_categories(self):
        """Test categories endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/categories")
            success = response.status_code == 200
            if success:
                data = response.json()
                categories = data.get('categories', [])
                success = len(categories) > 0
                expected_categories = ["Men's Wear", "Women's Wear", "Children's Wear", "Underwear"]
                category_names = [cat.get('name') for cat in categories]
                
                for expected in expected_categories:
                    if expected not in category_names:
                        success = False
                        break
                
                self.log_test("Get Categories", success, 
                             f"Found {len(categories)} categories: {category_names}")
            else:
                self.log_test("Get Categories", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Get Categories", False, str(e))
            return False, {}

    def test_get_products(self):
        """Test products endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/products")
            success = response.status_code == 200
            if success:
                data = response.json()
                products = data.get('products', [])
                success = len(products) > 0
                self.log_test("Get All Products", success, 
                             f"Found {len(products)} products")
            else:
                self.log_test("Get All Products", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
            return success, response.json() if success else {}
        except Exception as e:
            self.log_test("Get All Products", False, str(e))
            return False, {}

    def test_get_products_by_category(self, category_id):
        """Test products filtered by category"""
        try:
            response = self.session.get(f"{self.base_url}/api/products?category_id={category_id}")
            success = response.status_code == 200
            if success:
                data = response.json()
                products = data.get('products', [])
                # Check that all products belong to the specified category
                for product in products:
                    if product.get('category_id') != category_id:
                        success = False
                        break
                self.log_test("Get Products by Category", success, 
                             f"Found {len(products)} products for category {category_id}")
            else:
                self.log_test("Get Products by Category", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
            return success
        except Exception as e:
            self.log_test("Get Products by Category", False, str(e))
            return False

    def test_get_single_product(self, product_id):
        """Test getting a single product"""
        try:
            response = self.session.get(f"{self.base_url}/api/products/{product_id}")
            success = response.status_code == 200
            if success:
                data = response.json()
                product = data.get('product', {})
                success = product.get('id') == product_id
                self.log_test("Get Single Product", success, 
                             f"Product: {product.get('name', 'Unknown')}")
            else:
                self.log_test("Get Single Product", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
            return success
        except Exception as e:
            self.log_test("Get Single Product", False, str(e))
            return False

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        test_user = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/register", json=test_user)
            success = response.status_code == 201
            if success:
                data = response.json()
                user = data.get('user', {})
                success = user.get('username') == test_user['username']
                self.log_test("User Registration", success, 
                             f"Created user: {user.get('username')}")
                return success, test_user
            else:
                self.log_test("User Registration", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
                return False, {}
        except Exception as e:
            self.log_test("User Registration", False, str(e))
            return False, {}

    def test_user_login(self, user_credentials):
        """Test user login"""
        login_data = {
            "email": user_credentials.get('email'),
            "password": user_credentials.get('password')
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/login", json=login_data)
            success = response.status_code == 200
            if success:
                data = response.json()
                user = data.get('user', {})
                success = user.get('email') == login_data['email']
                self.log_test("User Login", success, 
                             f"Logged in user: {user.get('username')}")
            else:
                self.log_test("User Login", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
            return success
        except Exception as e:
            self.log_test("User Login", False, str(e))
            return False

    def test_check_auth(self):
        """Test authentication check"""
        try:
            response = self.session.get(f"{self.base_url}/api/check-auth")
            success = response.status_code == 200
            if success:
                data = response.json()
                authenticated = data.get('authenticated', False)
                self.log_test("Check Authentication", success, 
                             f"Authenticated: {authenticated}")
            else:
                self.log_test("Check Authentication", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
            return success
        except Exception as e:
            self.log_test("Check Authentication", False, str(e))
            return False

    def test_get_profile(self):
        """Test get user profile"""
        try:
            response = self.session.get(f"{self.base_url}/api/profile")
            success = response.status_code == 200
            if success:
                data = response.json()
                user = data.get('user', {})
                success = 'id' in user and 'username' in user
                self.log_test("Get Profile", success, 
                             f"Profile for: {user.get('username', 'Unknown')}")
            else:
                self.log_test("Get Profile", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
            return success
        except Exception as e:
            self.log_test("Get Profile", False, str(e))
            return False

    def test_update_profile(self):
        """Test update user profile"""
        update_data = {
            "full_name": "Updated Test User"
        }
        
        try:
            response = self.session.put(f"{self.base_url}/api/profile", json=update_data)
            success = response.status_code == 200
            if success:
                data = response.json()
                user = data.get('user', {})
                success = user.get('full_name') == update_data['full_name']
                self.log_test("Update Profile", success, 
                             f"Updated full name to: {user.get('full_name')}")
            else:
                self.log_test("Update Profile", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
            return success
        except Exception as e:
            self.log_test("Update Profile", False, str(e))
            return False

    def test_logout(self):
        """Test user logout"""
        try:
            response = self.session.post(f"{self.base_url}/api/logout")
            success = response.status_code == 200
            if success:
                data = response.json()
                success = "Logout successful" in data.get('message', '')
                self.log_test("User Logout", success, "Logged out successfully")
            else:
                self.log_test("User Logout", False, 
                             f"Status: {response.status_code}, Response: {response.text}")
            return success
        except Exception as e:
            self.log_test("User Logout", False, str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting StyleSphere API Tests...")
        print("=" * 50)
        
        # Test basic endpoints
        if not self.test_api_root():
            print("❌ API root failed, stopping tests")
            return self.get_results()
        
        # Test categories
        categories_success, categories_data = self.test_get_categories()
        if not categories_success:
            print("❌ Categories endpoint failed")
            return self.get_results()
        
        # Test products
        products_success, products_data = self.test_get_products()
        if not products_success:
            print("❌ Products endpoint failed")
            return self.get_results()
        
        # Test category filtering
        if categories_data.get('categories'):
            first_category = categories_data['categories'][0]
            self.test_get_products_by_category(first_category['id'])
        
        # Test single product
        if products_data.get('products'):
            first_product = products_data['products'][0]
            self.test_get_single_product(first_product['id'])
        
        # Test authentication flow
        registration_success, user_credentials = self.test_user_registration()
        if registration_success:
            # Test login with the registered user
            if self.test_user_login(user_credentials):
                # Test authenticated endpoints
                self.test_check_auth()
                self.test_get_profile()
                self.test_update_profile()
                self.test_logout()
        
        return self.get_results()

    def get_results(self):
        """Get test results summary"""
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed")
            failed_tests = [test for test in self.test_results if not test['success']]
            print("\nFailed tests:")
            for test in failed_tests:
                print(f"  - {test['test']}: {test['details']}")
            return 1

def main():
    tester = StyleSphereAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())