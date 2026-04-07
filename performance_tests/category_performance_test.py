import random
import string
import time
import sys
import os

# Allow running as: python -m performance_tests.category_performance_test
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_library import CategoryAPI
from performance_tests.performance_general import BasePerformanceTester


class CategoryPerformanceTester(BasePerformanceTester):
    def __init__(self, base_url="http://localhost:4567"):
        # Targeting the specific JAR process for isolated monitoring
        super().__init__(jar_name="runTodoManagerRestAPI-1.5.5.jar")
        self.api = CategoryAPI(base_url)

    def generate_random_category(self):
        title = ''.join(random.choices(
            string.ascii_letters + string.digits, k=20))
        description = ''.join(random.choices(
            string.ascii_letters + string.digits, k=50))
        return {"title": title, "description": description}

    def warm_up(self, count=20):
        print(f"Warming up with {count} objects...")
        warmup_ids = []
        for _ in range(count):
            resp = self.api.create_category(self.generate_random_category())
            if resp.status_code in [200, 201]:
                warmup_ids.append(resp.json()['id'])
        for i in warmup_ids:
            self.api.update_category_put(i, self.generate_random_category())
            self.api.delete_category(i)
        print("Warm-up complete.\n")

    def run_incremental_suite(self, max_objects=500, step=20):
        results = []
        current_ids = []

        print(
            f"Starting Incremental Test: 0 to {max_objects} (Step: {step})")

        try:
            for count in range(step, max_objects + step, step):
                # 1. FILL: Add (step - 1) objects to reach the new scale
                for _ in range(step - 1):
                    resp = self.api.create_category(self.generate_random_category())
                    if resp.status_code in [200, 201]:
                        current_ids.append(resp.json()['id'])

                # 2. MEASURE: The Nth object (the 'step-th' one of this batch)
                iterations = 3  # Small average to keep the test moving
                t_create, t_update, t_delete = 0, 0, 0
                start_monitor = time.time()

                for _ in range(iterations):
                    # Time Create
                    p = self.generate_random_category()
                    t0 = time.perf_counter()
                    r = self.api.create_category(p)
                    t_create += (time.perf_counter() - t0)

                    if r.status_code in [200, 201]:
                        nid = r.json()['id']
                        # Time Update
                        t0 = time.perf_counter()
                        self.api.update_category_put(
                            nid, self.generate_random_category())
                        t_update += (time.perf_counter() - t0)
                        # Time Delete
                        t0 = time.perf_counter()
                        self.api.delete_category(nid)
                        t_delete += (time.perf_counter() - t0)

                avg_res = self.monitor_resources(time.time() - start_monitor)

                results.append({
                    'num_objects': count,
                    'create_time': t_create / iterations, 'create_cpu': avg_res['cpu_avg'], 'create_mem': avg_res['mem_avg'],
                    'update_time': t_update / iterations, 'update_cpu': avg_res['cpu_avg'], 'update_mem': avg_res['mem_avg'],
                    'delete_time': t_delete / iterations, 'delete_cpu': avg_res['cpu_avg'], 'delete_mem': avg_res['mem_avg']
                })
                print(f"Milestone {count}/{max_objects} recorded.")

        finally:
            print("Cleaning up...")
            for i in current_ids:
                self.api.delete_category(i)

        return results


if __name__ == "__main__":
    tester = CategoryPerformanceTester()
    tester.warm_up()

    # Generates 100 data points (2000 / 20)
    final_results = tester.run_incremental_suite(max_objects=2000, step=20)

    tester.save_results(final_results, prefix="category_incremental")
    tester.plot_results(final_results, prefix="category_incremental")
