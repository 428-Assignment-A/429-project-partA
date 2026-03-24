import time
import psutil
import json
import os
import matplotlib.pyplot as plt


class BasePerformanceTester:
    def __init__(self, jar_name="runTodoManagerRestAPI-1.5.5.jar", base_output_dir='results'):
        self.base_output_dir = base_output_dir
        self.target_process = self._find_process(jar_name)
        if self.target_process:
            print(
                f"🎯 Targeted monitoring active for PID: {self.target_process.pid}")

    def _find_process(self, name):
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any(name in arg for arg in proc.info['cmdline']):
                    return psutil.Process(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def _get_path(self, prefix):
        path = os.path.join(self.base_output_dir, prefix)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def monitor_resources(self, duration=0.1):
        cpu_usages, mem_usages = [], []
        start_time = time.time()
        if duration < 0.1:
            duration = 0.1

        while time.time() - start_time < duration:
            if self.target_process and self.target_process.is_running():
                cpu_usages.append(
                    self.target_process.cpu_percent(interval=None))
                mem_usages.append(
                    self.target_process.memory_info().rss / (1024**2))
            else:
                cpu_usages.append(psutil.cpu_percent(interval=None))
                mem_usages.append(
                    psutil.virtual_memory().available / (1024**3))
            time.sleep(0.02)

        return {
            'cpu_avg': sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0,
            'mem_avg': sum(mem_usages) / len(mem_usages) if mem_usages else 0
        }

    def save_results(self, results, prefix="item"):
        folder = self._get_path(prefix)
        with open(os.path.join(folder, f"{prefix}_results.json"), 'w') as f:
            json.dump(results, f, indent=2)

    def plot_results(self, results, prefix="item"):
        folder = self._get_path(prefix)
        mem_unit = 'MB' if self.target_process else 'GB'
        metrics = {'time': 'Time (s)', 'cpu': 'CPU (%)',
                   'mem': f'Mem ({mem_unit})'}
        num_objects = [r['num_objects'] for r in results]

        for metric, ylabel in metrics.items():
            plt.figure(figsize=(10, 6))
            for action in ['create', 'update', 'delete']:
                key = f"{action}_{metric}"
                if key in results[0]:
                    plt.plot(num_objects, [r[key]
                             for r in results], label=action, marker='o')
            plt.xlabel('Objects')
            plt.ylabel(ylabel)
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(folder, f"{prefix}_{metric}.png"))
            plt.close()
