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
        else:
            print(
                f"⚠️ Warning: Could not find process for {jar_name}. Monitoring system-wide instead.")

    def _find_process(self, name):
        """Finds the PID of the Java process running the specific JAR."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                # Check if it's a java process and if our JAR is in the command line
                if proc.info['cmdline'] and any(name in arg for arg in proc.info['cmdline']):
                    return psutil.Process(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def _get_path(self, prefix):
        """Creates and returns the specific path for results."""
        path = os.path.join(self.base_output_dir, prefix)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def monitor_resources(self, duration=0.1):
        """Monitors CPU and Memory. Uses process-specific data if target is found."""
        cpu_usages = []
        mem_usages = []
        start_time = time.time()

        if duration < 0.1:
            duration = 0.1

        while time.time() - start_time < duration:
            if self.target_process and self.target_process.is_running():
                # Process-specific CPU (interval=None for non-blocking)
                cpu_usages.append(
                    self.target_process.cpu_percent(interval=None))
                # Memory in MB (RSS is actual physical memory used)
                mem_usages.append(
                    self.target_process.memory_info().rss / (1024**2))
            else:
                # Fallback to system-wide
                cpu_usages.append(psutil.cpu_percent(interval=None))
                mem_usages.append(
                    psutil.virtual_memory().available / (1024**3))
            time.sleep(0.05)

        return {
            'cpu_avg': sum(cpu_usages) / len(cpu_usages) if cpu_usages else 0,
            'mem_avg': sum(mem_usages) / len(mem_usages) if mem_usages else 0
        }

    def save_results(self, results, prefix="item"):
        """Saves JSON results."""
        folder = self._get_path(prefix)
        save_path = os.path.join(folder, f"{prefix}_performance_results.json")
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ JSON saved to {save_path}")

    def plot_results(self, results, prefix="item"):
        """Generates charts. Adjusts labels based on whether process-specific data was used."""
        folder = self._get_path(prefix)
        mem_label = 'Memory Usage (MB)' if self.target_process else 'Available Memory (GB)'

        metrics = {
            'time': 'Transaction Time (s)',
            'cpu': 'CPU Usage (%)',
            'mem': mem_label
        }

        num_objects = [r['num_objects'] for r in results]

        for metric, ylabel in metrics.items():
            plt.figure(figsize=(10, 6))
            for action in ['create', 'update', 'delete']:
                key = f"{action}_{metric}"
                if key in results[0]:
                    plt.plot(num_objects, [r[key] for r in results],
                             label=f'{action.capitalize()}', marker='o')

            plt.xlabel('Number of Objects')
            plt.ylabel(ylabel)
            plt.title(f"{prefix.upper()} Performance - {ylabel}")
            plt.legend()
            plt.grid(True)
            save_path = os.path.join(folder, f"{prefix}_{metric}_usage.png")
            plt.savefig(save_path)
            plt.close()
        print(f"Charts saved to {folder}/")
