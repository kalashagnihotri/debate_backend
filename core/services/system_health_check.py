#!/usr/bin/env python3
"""
Comprehensive System Health Check for Online Debate Platform.

This module provides comprehensive testing of all platform components including
backend, frontend, WebSocket connections, authentication, and performance metrics.
Tests are designed to verify system integrity and identify potential issues.
"""

import asyncio
import json
import socket
import subprocess
import time
from datetime import datetime

import requests
import websockets


class SystemHealthChecker:
    """
    Comprehensive health checker for the debate platform.

    This class performs various health checks on different components
    of the online debate platform to ensure all systems are operational.
    """

    def __init__(self):
        """Initialize the health checker with default configuration."""
        self.api_base = "http://127.0.0.1:8000/api/v1"
        self.frontend_base = "http://127.0.0.1:3000"
        self.ws_base = "ws://127.0.0.1:8001"
        self.session = requests.Session()
        self.results = {}

    def print_header(self, title: str) -> None:
        """
        Print a formatted header for test sections.

        Args:
            title: The section title to display
        """
        print("\n" + "=" * 70)
        print(f"🏥 {title}")
        print("=" * 70)

    def print_result(
        self, component: str, test_name: str, success: bool, details: str = ""
    ) -> None:
        """
        Print and record a test result.

        Args:
            component: The component being tested
            test_name: Name of the specific test
            success: Whether the test passed
            details: Additional details about the test result
        """
        status = "✅" if success else "❌"
        print(f"{status} {component}: {test_name}")
        if details:
            print(f"   {details}")

        if component not in self.results:
            self.results[component] = []
        self.results[component].append(
            {"test": test_name, "success": success, "details": details}
        )

    def check_port_availability(self, host: str, port: int, service_name: str) -> bool:
        """
        Check if a port is available and responding.

        Args:
            host: The hostname to check
            port: The port number to check
            service_name: Human-readable service name for reporting

        Returns:
            bool: True if port is available, False otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                self.print_result(
                    "Network",
                    f"{service_name} Port {port}",
                    True,
                    f"Port {port} is open",
                )
                return True
            else:
                self.print_result(
                    "Network",
                    f"{service_name} Port {port}",
                    False,
                    f"Port {port} is closed",
                )
                return False
        except Exception as e:
            self.print_result("Network", f"{service_name} Port {port}", False, str(e))
            return False

    def test_django_backend(self):
        """Test Django backend health."""
        self.print_header("Django Backend Health Check")

        # Test basic connectivity
        try:
            response = self.session.get(f"{self.api_base}/debates/topics/", timeout=5)
            success = response.status_code == 200
            self.print_result(
                "Django", "API Connectivity", success, f"Status: {response.status_code}"
            )

            if success:
                topics = response.json()
                self.print_result(
                    "Django", "Data Retrieval", True, f"Retrieved {len(topics)} topics"
                )
        except Exception as e:
            self.print_result("Django", "API Connectivity", False, str(e))

        # Test database connectivity
        try:
            response = self.session.get(f"{self.api_base}/debates/sessions/", timeout=5)
            success = response.status_code == 200
            self.print_result(
                "Django",
                "Database Connection",
                success,
                f"Status: {response.status_code}",
            )
        except Exception as e:
            self.print_result("Django", "Database Connection", False, str(e))

    def test_authentication_system(self):
        """Test authentication system."""
        self.print_header("Authentication System Health Check")

        # Test user registration
        try:
            user_data = {
                "username": f"healthcheck_{int(time.time())}",
                "email": f"healthcheck_{int(time.time())}@test.com",
                "password": "testpass123",
                "role": "student",
            }

            response = self.session.post(
                f"{self.api_base}/users/register/", json=user_data
            )
            success = response.status_code == 201
            self.print_result(
                "Auth", "User Registration", success, f"Status: {response.status_code}"
            )

            if success:
                # Test login
                login_data = {
                    "username": user_data["username"],
                    "password": user_data["password"],
                }

                response = self.session.post(f"{self.api_base}/token/", json=login_data)
                if response.status_code == 200:
                    tokens = response.json()
                    access_token = tokens.get("access")
                    refresh_token = tokens.get("refresh")

                    self.print_result(
                        "Auth",
                        "JWT Token Generation",
                        True,
                        f"Access: {bool(access_token)}, Refresh: {bool(refresh_token)}",
                    )

                    # Test protected endpoint access
                    if access_token:
                        headers = {"Authorization": f"Bearer {access_token}"}
                        response = self.session.get(
                            f"{self.api_base}/users/profile/", headers=headers
                        )
                        success = response.status_code == 200
                        self.print_result(
                            "Auth",
                            "Protected Endpoint Access",
                            success,
                            f"Status: {response.status_code}",
                        )

                        return access_token
                else:
                    self.print_result(
                        "Auth",
                        "JWT Token Generation",
                        False,
                        f"Status: {response.status_code}",
                    )

        except Exception as e:
            self.print_result("Auth", "Authentication Flow", False, str(e))

        return None

    async def test_websocket_system(self, access_token=None):
        """Test WebSocket system."""
        self.print_header("WebSocket System Health Check")

        if not access_token:
            self.print_result(
                "WebSocket", "Authentication Token", False, "No access token provided"
            )
            return

        try:
            # Test WebSocket connection
            ws_url = f"{self.ws_base}/ws/debates/2/?token={access_token}"

            websocket = await websockets.connect(ws_url)
            self.print_result(
                "WebSocket", "Connection Establishment", True, "Connected successfully"
            )

            # Test message sending
            message_data = {
                "type": "chat_message",
                "message": "Health check message",
                "session_id": 2,
            }

            await websocket.send(json.dumps(message_data))
            self.print_result(
                "WebSocket", "Message Sending", True, "Message sent successfully"
            )

            # Test message receiving
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=3.0)
                data = json.loads(response)
                self.print_result(
                    "WebSocket",
                    "Message Receiving",
                    True,
                    f"Received: {data.get('type')}",
                )
            except asyncio.TimeoutError:
                self.print_result(
                    "WebSocket",
                    "Message Receiving",
                    False,
                    "Timeout waiting for response",
                )

            await websocket.close()

        except Exception as e:
            self.print_result("WebSocket", "Connection", False, str(e))

    def test_frontend_system(self):
        """Test frontend system."""
        self.print_header("Frontend System Health Check")

        try:
            # Test frontend availability
            response = self.session.get(self.frontend_base, timeout=5)
            success = response.status_code == 200
            self.print_result(
                "Frontend",
                "React App Availability",
                success,
                f"Status: {response.status_code}",
            )

            # Test if it's serving the React app
            if success and "react" in response.text.lower():
                self.print_result(
                    "Frontend", "React App Content", True, "React app detected"
                )
            elif success:
                self.print_result(
                    "Frontend", "React App Content", True, "Frontend serving content"
                )

        except Exception as e:
            self.print_result("Frontend", "Frontend Connection", False, str(e))

    def test_cors_configuration(self):
        """Test CORS configuration."""
        self.print_header("CORS Configuration Health Check")

        try:
            # Test preflight request
            response = self.session.options(
                f"{self.api_base}/debates/topics/",
                headers={
                    "Origin": self.frontend_base,
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization, Content-Type",
                },
            )

            success = response.status_code == 200
            self.print_result(
                "CORS", "Preflight Request", success, f"Status: {response.status_code}"
            )

            if success:
                cors_headers = {
                    "Access-Control-Allow-Origin": response.headers.get(
                        "Access-Control-Allow-Origin"
                    ),
                    "Access-Control-Allow-Methods": response.headers.get(
                        "Access-Control-Allow-Methods"
                    ),
                    "Access-Control-Allow-Headers": response.headers.get(
                        "Access-Control-Allow-Headers"
                    ),
                }

                for header, value in cors_headers.items():
                    self.print_result(
                        "CORS",
                        header.replace("Access-Control-Allow-", ""),
                        bool(value),
                        value or "Not set",
                    )

        except Exception as e:
            self.print_result("CORS", "CORS Configuration", False, str(e))

    def test_performance_metrics(self):
        """Test basic performance metrics."""
        self.print_header("Performance Metrics Health Check")

        # Test API response times
        endpoints = [
            ("/debates/topics/", "Topics API"),
            ("/debates/sessions/", "Sessions API"),
        ]

        for endpoint, name in endpoints:
            try:
                start_time = time.time()
                response = self.session.get(f"{self.api_base}{endpoint}")
                end_time = time.time()

                response_time = (end_time - start_time) * 1000  # milliseconds
                success = response.status_code == 200 and response_time < 1000

                self.print_result(
                    "Performance",
                    f"{name} Response Time",
                    success,
                    f"{response_time:.1f}ms",
                )

            except Exception as e:
                self.print_result("Performance", f"{name} Response Time", False, str(e))

    async def run_full_health_check(self):
        """Run complete system health check."""
        print("🏥 ONLINE DEBATE PLATFORM - SYSTEM HEALTH CHECK")
        print("=" * 70)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Testing API: {self.api_base}")
        print(f"🖥️  Testing Frontend: {self.frontend_base}")
        print(f"🔌 Testing WebSocket: {self.ws_base}")

        # Check port availability
        self.print_header("Network Connectivity Check")
        self.check_port_availability("127.0.0.1", 8000, "Django API")
        self.check_port_availability("127.0.0.1", 8001, "WebSocket")
        self.check_port_availability("127.0.0.1", 3000, "React Frontend")

        # Test all systems
        self.test_django_backend()
        access_token = self.test_authentication_system()
        await self.test_websocket_system(access_token)
        self.test_frontend_system()
        self.test_cors_configuration()
        self.test_performance_metrics()

        # Generate health report
        self.generate_health_report()

    def generate_health_report(self):
        """Generate comprehensive health report."""
        self.print_header("SYSTEM HEALTH REPORT")

        total_tests = 0
        passed_tests = 0

        for component, tests in self.results.items():
            component_passed = sum(1 for test in tests if test["success"])
            component_total = len(tests)
            total_tests += component_total
            passed_tests += component_passed

            success_rate = (
                (component_passed / component_total) * 100 if component_total > 0 else 0
            )
            status = (
                "🟢" if success_rate >= 80 else "🟡" if success_rate >= 60 else "🔴"
            )

            print(
                f"{status} {component}: {component_passed}/{component_total} tests passed ({success_rate:.1f}%)"
            )

        overall_success_rate = (
            (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        )
        overall_status = (
            "🟢 HEALTHY"
            if overall_success_rate >= 80
            else "🟡 WARNING" if overall_success_rate >= 60 else "🔴 CRITICAL"
        )

        print("\n" + "=" * 70)
        print(f"🏥 OVERALL SYSTEM STATUS: {overall_status}")
        print(
            f"📊 Total Tests: {passed_tests}/{total_tests} passed ({overall_success_rate:.1f}%)"
        )
        print("=" * 70)

        # Recommendations
        if overall_success_rate < 100:
            print("\n💡 RECOMMENDATIONS:")
            for component, tests in self.results.items():
                failed_tests = [test for test in tests if not test["success"]]
                if failed_tests:
                    print(f"\n🔧 {component}:")
                    for test in failed_tests:
                        print(f"   - Fix: {test['test']} - {test['details']}")

        return overall_success_rate >= 80


async def main():
    checker = SystemHealthChecker()
    await checker.run_full_health_check()


if __name__ == "__main__":
    asyncio.run(main())
