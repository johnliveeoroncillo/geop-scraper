import os

def create_directory_structure(client_name, job_title):
    base_folder = "output"
    client_folder = os.path.join(base_folder, client_name)
    job_folder = os.path.join(client_folder, job_title.replace(" ", "_"))
    
    os.makedirs(job_folder, exist_ok=True)
    os.makedirs(os.path.join(job_folder, "Before_Photos"), exist_ok=True)
    os.makedirs(os.path.join(job_folder, "After_Photos"), exist_ok=True)

    return job_folder
