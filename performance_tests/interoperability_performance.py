import random
import string
import time
from api_library import TodoAPI, ProjectAPI
from performance_tests.performance_general import BasePerformanceTester


class InteroperabilityPerformanceTester(BasePerformanceTester):
    def __init__(self, base_url="http://localhost:4567"):
        super().__init__(jar_name="runTodoManagerRestAPI-1.5.5.jar")
        self.todo_api = TodoAPI(base_url)
        self.project_api = ProjectAPI(base_url)
        self.base_url = base_url

    def generate_random_todo(self):
        title = ''.join(random.choices(
            string.ascii_letters + string.digits, k=20))
        description = ''.join(random.choices(
            string.ascii_letters + string.digits, k=50))
        return {"title": title, "description": description, "doneStatus": False}

    def generate_random_project(self):
        title = ''.join(random.choices(
            string.ascii_letters + string.digits, k=20))
        description = ''.join(random.choices(
            string.ascii_letters + string.digits, k=50))
        return {"title": title, "description": description, "completed": False, "active": True}

    def create_todo(self, payload):
        return self.todo_api.create_todo(payload)

    def create_project(self, payload):
        return self.project_api.create_project(payload)

    def link_todo_to_project(self, project_id, todo_id):
        return self.todo_api._make_request(
            "POST", f"/projects/{project_id}/tasks",
            json={"id": todo_id}
        )

    def unlink_todo_from_project(self, project_id, todo_id):
        return self.todo_api._make_request(
            "DELETE", f"/projects/{project_id}/tasks/{todo_id}"
        )

    def assign_category_to_todo(self, todo_id, category_id):
        return self.todo_api._make_request(
            "POST", f"/todos/{todo_id}/categories",
            json={"id": category_id}
        )

    def create_category(self, title):
        return self.todo_api._make_request(
            "POST", "/categories",
            json={"title": title}
        )

    def delete_todo(self, todo_id):
        return self.todo_api.delete_todo(todo_id)

    def delete_project(self, project_id):
        return self.project_api.delete_project(project_id)

    def delete_category(self, category_id):
        return self.todo_api._make_request("DELETE", f"/categories/{category_id}")

    def warm_up(self, count=20):
        print(f"Warming up with {count} interoperability pairs...")
        warmup_todo_ids = []
        warmup_project_ids = []
        for _ in range(count):
            t_resp = self.create_todo(self.generate_random_todo())
            p_resp = self.create_project(self.generate_random_project())
            if t_resp.status_code in [200, 201] and p_resp.status_code in [200, 201]:
                tid = t_resp.json()['id']
                pid = p_resp.json()['id']
                warmup_todo_ids.append(tid)
                warmup_project_ids.append(pid)
                self.link_todo_to_project(pid, tid)
                self.unlink_todo_from_project(pid, tid)
        for tid in warmup_todo_ids:
            self.delete_todo(tid)
        for pid in warmup_project_ids:
            self.delete_project(pid)
        print("Warm-up complete.\n")

    def run_incremental_suite(self, max_objects=500, step=20):
        results = []
        current_todo_ids = []
        current_project_ids = []
        current_category_ids = []

        print(f"Starting Incremental Test: 0 to {max_objects} (Step: {step})")

        try:
            for count in range(step, max_objects + step, step):
                for _ in range(step - 1):
                    t_resp = self.create_todo(self.generate_random_todo())
                    p_resp = self.create_project(self.generate_random_project())
                    c_resp = self.create_category(
                        ''.join(random.choices(string.ascii_letters, k=10))
                    )
                    if t_resp.status_code in [200, 201]:
                        current_todo_ids.append(t_resp.json()['id'])
                    if p_resp.status_code in [200, 201]:
                        current_project_ids.append(p_resp.json()['id'])
                    if c_resp.status_code in [200, 201]:
                        current_category_ids.append(c_resp.json()['id'])

                iterations = 3
                t_create, t_update, t_delete = 0, 0, 0
                start_monitor = time.time()

                for _ in range(iterations):
                    t_resp = self.create_todo(self.generate_random_todo())
                    p_resp = self.create_project(self.generate_random_project())

                    if t_resp.status_code in [200, 201] and p_resp.status_code in [200, 201]:
                        tid = t_resp.json()['id']
                        pid = p_resp.json()['id']

                        t0 = time.perf_counter()
                        self.link_todo_to_project(pid, tid)
                        t_create += (time.perf_counter() - t0)

                        c_resp = self.create_category(
                            ''.join(random.choices(string.ascii_letters, k=10))
                        )
                        if c_resp.status_code in [200, 201]:
                            cid = c_resp.json()['id']
                            t0 = time.perf_counter()
                            self.assign_category_to_todo(tid, cid)
                            t_update += (time.perf_counter() - t0)
                            self.delete_category(cid)

                        t0 = time.perf_counter()
                        self.unlink_todo_from_project(pid, tid)
                        t_delete += (time.perf_counter() - t0)

                        self.delete_todo(tid)
                        self.delete_project(pid)

                avg_res = self.monitor_resources(time.time() - start_monitor)

                results.append({
                    'num_objects': count,
                    'create_time': t_create / iterations,
                    'create_cpu': avg_res['cpu_avg'],
                    'create_mem': avg_res['mem_avg'],
                    'update_time': t_update / iterations,
                    'update_cpu': avg_res['cpu_avg'],
                    'update_mem': avg_res['mem_avg'],
                    'delete_time': t_delete / iterations,
                    'delete_cpu': avg_res['cpu_avg'],
                    'delete_mem': avg_res['mem_avg'],
                })
                print(f"Milestone {count}/{max_objects} recorded.")

        finally:
            print("Cleaning up...")
            for tid in current_todo_ids:
                self.delete_todo(tid)
            for pid in current_project_ids:
                self.delete_project(pid)
            for cid in current_category_ids:
                self.delete_category(cid)

        return results


if __name__ == "__main__":
    tester = InteroperabilityPerformanceTester()
    tester.warm_up()

    final_results = tester.run_incremental_suite(max_objects=2000, step=20)

    tester.save_results(final_results, prefix="interoperability_incremental")
    tester.plot_results(final_results, prefix="interoperability_incremental")
