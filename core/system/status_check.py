import asyncio
import json
import time
from datetime import datetime

import requests
import websockets


class SystemStatusChecker:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.websocket_url = "ws://127.0.0.1:8001"
        self.access_token = None
        self.checks = []

    def add_check(self, name, status, details="", performance=""):
        """Add a system check result"""
        self.checks.append({
            'name': name,
            'status': status,
            'details': details,
            'performance': performance,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })

    def login(self):
        """Test JWT authentication"""
        try:
            response = requests.post(f"{self.base_url}/api/v1/token/", json={
                "username": "testuser",
                "password": "testpass123"
            }, timeout=5)

            if response.status_code == 200:
                self.access_token = response.json()['access']
                self.add_check(
                    "JWT Authentication",
                    "✅ PASS",
                    "Successfully obtained access token")
                return True
            else:
                self.add_check(
                    "JWT Authentication", "❌ FAIL", f"Status: {
                        response.status_code}")
                return False
        except Exception as e:
            self.add_check("JWT Authentication", "❌ FAIL", f"Exception: {e}")
            return False

    def check_django_server(self):
        """Check Django API server"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/v1/debates/topics/", timeout=5)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                self.add_check(
                    "Django API Server",
                    "✅ PASS",
                    f"Topics endpoint working. Found {len(data)} topics",
                    f"{response_time:.2f}ms"
                )
                return True
            else:
                self.add_check(
                    "Django API Server", "❌ FAIL", f"Status: {
                        response.status_code}")
                return False
        except Exception as e:
            self.add_check("Django API Server", "❌ FAIL", f"Exception: {e}")
            return False

    def check_daphne_server(self):
        """Check Daphne WebSocket server"""
        try:
            response = requests.get("\1", timeout=5)
            if response.status_code == 404:  # 404 is expected for root path
                self.add_check(
                    "Daphne WebSocket Server",
                    "✅ PASS",
                    "Server responding (404 expected for root)")
                return True
            else:
                self.add_check(
                    "Daphne WebSocket Server",
                    "⚠️ WARN",
                    f"Unexpected status: {
                        response.status_code}")
                return False
        except Exception as e:
            self.add_check("Daphne WebSocket Server", "❌ FAIL", f"Exception: {e}")
            return False

    async def check_websocket_connection(self):
        """Test WebSocket connection"""
        if not self.access_token:
            self.add_check(
                "WebSocket Connection",
                "❌ FAIL",
                "No access token available")
            return False

        try:
            websocket_url = f"{self.websocket_url}/ws/debates/6/?token={self.access_token}"

            start_time = time.time()
            async with websockets.connect(websocket_url, timeout=5) as websocket:
                # Send test message
                test_message = {"type": "chat_message", "message": "System check test"}
                await websocket.send(json.dumps(test_message))

                # Wait for response
                await asyncio.wait_for(websocket.recv(), timeout=3.0)
                connection_time = (time.time() - start_time) * 1000

                self.add_check(
                    "WebSocket Connection",
                    "✅ PASS",
                    "Successfully connected and exchanged messages",
                    f"{connection_time:.2f}ms"
                )
                return True

        except Exception as e:
            self.add_check("WebSocket Connection", "❌ FAIL", f"Exception: {e}")
            return False

    def check_database_operations(self):
        """Test database operations through API"""
        try:
            # Test read operations
            start_time = time.time()
            response = requests.get(
                f"{self.base_url}/api/v1/debates/sessions/", timeout=5)
            read_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                sessions = response.json()
                self.add_check(
                    "Database Read Operations",
                    "✅ PASS",
                    f"Successfully read {len(sessions)} sessions",
                    f"{read_time:.2f}ms"
                )
                return True
            else:
                self.add_check(
                    "Database Read Operations",
                    "❌ FAIL",
                    f"Status: {
                        response.status_code}")
                return False
        except Exception as e:
            self.add_check("Database Read Operations", "❌ FAIL", f"Exception: {e}")
            return False

    def check_cors_configuration(self):
        """Test CORS configuration"""
        try:
            response = requests.options(
                f"{self.base_url}/api/v1/debates/topics/",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                },
                timeout=5
            )

            cors_headers = response.headers.get('Access-Control-Allow-Origin')
            if cors_headers:
                self.add_check(
                    "CORS Configuration",
                    "✅ PASS",
                    f"CORS headers present: {cors_headers}"
                )
                return True
            else:
                self.add_check("CORS Configuration", "❌ FAIL", "No CORS headers found")
                return False
        except Exception as e:
            self.add_check("CORS Configuration", "❌ FAIL", f"Exception: {e}")
            return False

    def check_api_endpoints(self):
        """Test various API endpoints"""
        endpoints = [
            ("Topics", "/api/v1/debates/topics/", False),
            ("Sessions", "/api/v1/debates/sessions/", False),
            ("Users", "/api/v1/users/", True),
            ("Token Refresh", "/api/v1/token/refresh/", False),
        ]

        headers = {
            "Authorization": f"Bearer {
                self.access_token}"} if self.access_token else {}

        for name, endpoint, requires_auth in endpoints:
            try:
                start_time = time.time()
                request_headers = headers if requires_auth else {}
                response = requests.get(
                    f"{self.base_url}{endpoint}", headers=request_headers, timeout=5)
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    self.add_check(
                        f"API Endpoint: {name}",
                        "✅ PASS",
                        "\1",
                        f"{response_time:.2f}ms"
                    )
                elif response.status_code == 401 and requires_auth and not self.access_token:
                    self.add_check(
                        f"API Endpoint: {name}",
                        "⚠️ WARN",
                        "Authentication required (expected)")
                else:
                    self.add_check(
                        f"API Endpoint: {name}", "❌ FAIL", f"Status: {
                            response.status_code}")
            except Exception as e:
                self.add_check(f"API Endpoint: {name}", "❌ FAIL", f"Exception: {e}")

    def check_frontend_server(self):
        """Check if frontend server is running"""
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                self.add_check(
                    "Frontend Server",
                    "✅ PASS",
                    "React development server running")
                return True
            else:
                self.add_check(
                    "Frontend Server", "❌ FAIL", f"Status: {
                        response.status_code}")
                return False
        except Exception as e:
            self.add_check("Frontend Server", "❌ FAIL", f"Connection failed: {e}")
            return False

    def generate_status_report(self):
        """Generate comprehensive status report"""
        print("\n" + "=" * 80)
        print("🏥 ONLINE DEBATE PLATFORM - SYSTEM STATUS REPORT")
        print("=" * 80)
        print(f"📅 Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔍 Total Checks: {len(self.checks)}")

        # Count status types
        passed = len([c for c in self.checks if "✅" in c['status']])
        failed = len([c for c in self.checks if "❌" in c['status']])
        warnings = len([c for c in self.checks if "⚠️" in c['status']])

        print(f"✅ Passed: {passed} | ❌ Failed: {failed} | ⚠️ Warnings: {warnings}")

        # Overall system health
        if failed == 0:
            if warnings == 0:
                health_status = "🟢 EXCELLENT"
            else:
                health_status = "🟡 GOOD"
        else:
            health_status = "🔴 NEEDS ATTENTION"

        print(f"🏥 Overall System Health: {health_status}")
        print("\n" + "-" * 80)
        print("📋 DETAILED CHECK RESULTS")
        print("-" * 80)

        for check in self.checks:
            print(f"[{check['timestamp']}] {check['status']} {check['name']}")
            if check['details']:
                print(f"    📝 {check['details']}")
            if check['performance']:
                print(f"    ⚡ Performance: {check['performance']}")
            print()

        # Performance summary
        performance_checks = [c for c in self.checks if c['performance']]
        if performance_checks:
            print("-" * 80)
            print("⚡ PERFORMANCE SUMMARY")
            print("-" * 80)
            for check in performance_checks:
                print(f"  {check['name']}: {check['performance']}")

        print("\n" + "=" * 80)
        return health_status

    async def run_comprehensive_check(self):
        """Run all system checks"""
        print("🔍 Starting Comprehensive System Status Check...")
        print("=" * 60)

        # Core system checks
        print("1️⃣ Checking authentication...")
        self.login()

        print("2️⃣ Checking Django API server...")
        self.check_django_server()

        print("3️⃣ Checking Daphne WebSocket server...")
        self.check_daphne_server()

        print("4️⃣ Checking WebSocket connection...")
        await self.check_websocket_connection()

        print("5️⃣ Checking database operations...")
        self.check_database_operations()

        print("6️⃣ Checking CORS configuration...")
        self.check_cors_configuration()

        print("7️⃣ Checking API endpoints...")
        self.check_api_endpoints()

        print("8️⃣ Checking frontend server...")
        self.check_frontend_server()

        # Generate final report
        health_status = self.generate_status_report()

        return health_status


async def main():
    checker = SystemStatusChecker()
    health_status = await checker.run_comprehensive_check()

    # Exit with appropriate code
    if "EXCELLENT" in health_status or "GOOD" in health_status:
        print("🎉 System is ready for production!")
        return 0
    else:
        print("⚠️ System requires attention before production deployment.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
