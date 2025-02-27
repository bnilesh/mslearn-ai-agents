from datetime import datetime
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class devops_plugin:
    """A plugin that performs developer operation tasks."""
    
    @kernel_function(description="Appends a string to the given log file and saves it")
    def append_to_log_file(self, filepath: str, content: str) -> None:
        with open(filepath, 'a', encoding='utf-8') as file:
            file.write(content + '\n')


    @kernel_function(description="A function that restarts the provided service")
    def restart_service(self, service_name: str = "", logfile: str = "") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

        msg = f"""
        [{timestamp}] ALERT  DevopsManager: Multiple failures detected in {service_name}. Restarting service.
        [{timestamp}] INFO  {service_name}: Restart initiated.
        [{timestamp}] INFO  {service_name}: Service restarted successfully
        """
        self.append_to_log_file(logfile, msg)
        return f"Service {service_name} restarted successfully."

    @kernel_function(description="")
    def rollback_transaction(self, logfile: str = "") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

        msg = f"""
        [{timestamp}] ALERT  DevopsManager: Transaction failure detected. Rolling back transaction batch.
        [{timestamp}] INFO   TransactionProcessor: Rolling back transaction batch.
        [{timestamp}] INFO   TransactionProcessor: Transaction rollback completed successfully.
        """
        self.append_to_log_file(logfile, msg)
        return "Transaction rolled back successfully."

    @kernel_function(description="")
    def redeploy_resource(self, resource_name: str = "", logfile: str = "") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        msg = f"""
        [{timestamp}] ALERT  DevopsManager: Resource deployment failure detected in '{resource_name}'. Redeploying resource.
        [{timestamp}] INFO   DeploymentManager: Redeployment request submitted.
        [{timestamp}] INFO   DeploymentManager: Service successfully redeployed, resource '{resource_name}' created successfully.
        """
        self.append_to_log_file(logfile, msg)
        return f"Resource '{resource_name}' redeployed successfully."

    @kernel_function(description="")
    def increase_quota(self, logfile: str = "") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

        msg = f"""
        [{timestamp}] ALERT  DevopsManager: High request volume detected. Increasing quota.
        [{timestamp}] INFO   APIManager: Quota increase request submitted.
        [{timestamp}] INFO   APIManager: Quota successfully increased to 150% of previous limit.
        """
        self.append_to_log_file(logfile, msg)
        return "Successfully increased quota."

    @kernel_function(description="")
    def escalate_issue(self, logfile: str = "") -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        
        msg = f"""
        [{timestamp}] ALERT  DevopsManager: Cannot resolve issue.
        [{timestamp}] ALERT  DevopsManager: Requesting escalation.
        """
        self.append_to_log_file(logfile, msg)
        return "Submitted escalation request."
        
            