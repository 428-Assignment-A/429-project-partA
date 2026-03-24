import random
import string
import time
from api_library import TodoAPI
from .performance_general import BasePerformanceTester


class TodoPerformanceTester(BasePerformanceTester):
    def __init__(self, base_url="http://localhost:4567"):
        # Explicitly passing the JAR name to the base class for monitoring
        super().__init__(jar_name="runTodoManagerRestAPI-1.5.5.jar")
        self.api = TodoAPI(base_url)

    def generate_random_todo(self):
        """Generates random todo data for testing."""
        title = ''.join(random.choices(
            string.ascii_letters + string.digits, k=20))
        description = ''.join(random.choices(
            string.ascii_letters + string.digits, k=50))
        return {"title": title, "description": description, "doneStatus": False}

    def warm_up(self, count=20):
        """Primes the server and OS buffers before real testing begins."""
        print(f"🔥 Warming up with {count} objects...")
        warmup_ids = []
        for _ in range(count):
            resp = self.api.create_todo(self.generate_random_todo())
            if resp.status_code in [200, 201]:
                warmup_ids.append(resp.json()['id'])

        for i in warmup_ids:
            self.api.update_todo_put(i, self.generate_random_todo())
            self.api.delete_todo(i)
        print("✅ Warm-up complete. Starting experiments.\n")

    def run_experiment(self, target_count):
        print(f"--- Testing Nth object at scale: {target_count} ---")

        # 1. PRE-FILL: Populate the database to (target_count - 1)
        existing_ids = []
        for _ in range(target_count - 1):
            resp = self.api.create_todo(self.generate_random_todo())
            if resp.status_code in [200, 201]:
                existing_ids.append(resp.json()['id'])

        # 2. MEASURE (Average of 5 samples for high precision)
        iterations = 5
        total_create, total_update, total_delete = 0, 0, 0
        start_monitor = time.time()

        try:
            for _ in range(iterations):
                # CREATE - High Precision Monotonic Timer
                payload = self.generate_random_todo()
                t0 = time.perf_counter()
                resp = self.api.create_todo(payload)
                t1 = time.perf_counter()
                total_create += (t1 - t0)

                if resp.status_code in [200, 201]:
                    nth_id = resp.json()['id']

                    # UPDATE - High Precision
                    t0 = time.perf_counter()
                    self.api.update_todo_put(
                        nth_id, self.generate_random_todo())
                    t1 = time.perf_counter()
                    total_update += (t1 - t0)

                    # DELETE - High Precision
                    t0 = time.perf_counter()
                    self.api.delete_todo(nth_id)
                    t1 = time.perf_counter()
                    total_delete += (t1 - t0)

            avg_res = self.monitor_resources(time.time() - start_monitor)

        finally:
            # 3. CLEANUP: Clear pre-fill so next experiment starts fresh
            for i in existing_ids:
                self.api.delete_todo(i)

        return {
            'num_objects': target_count,
            'create_time': total_create / iterations, 'create_cpu': avg_res['cpu_avg'], 'create_mem': avg_res['mem_avg'],
            'update_time': total_update / iterations, 'update_cpu': avg_res['cpu_avg'], 'update_mem': avg_res['mem_avg'],
            'delete_time': total_delete / iterations, 'delete_cpu': avg_res['cpu_avg'], 'delete_mem': avg_res['mem_avg']
        }


if __name__ == "__main__":
    tester = TodoPerformanceTester()
    tester.warm_up()

    # Testing performance as the database size increases
    test_counts = [10, 500, 1000, 1500]
    results = [tester.run_experiment(count) for count in test_counts]

    tester.save_results(results, prefix="todo")
    tester.plot_results(results, prefix="todo")
