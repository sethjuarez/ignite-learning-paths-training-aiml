from azureml.core.model import Model
from azureml.core import Workspace, Environment
from azureml.core.conda_dependencies import CondaDependencies 
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AciWebservice

def main():
    # get access to workspace
    try:
        ws = Workspace.from_config()
        print(ws.name, ws.location, ws.resource_group, ws.location, sep='\t')
        print('Library configuration succeeded')
    except:
        print('Workspace not found')
        return


    # get model
    model = Model(ws, 'absa')

    # deploy model
    

    pip = ["azureml-defaults", 
            "azureml-monitoring", 
            "git+https://github.com/NervanaSystems/nlp-architect.git@absa", 
            "spacy==2.1.4"]

    myenv = CondaDependencies.create(pip_packages=pip)

    with open("absaenv.yml","w") as f:
        f.write(myenv.serialize_to_string())

    deploy_env = Environment.from_conda_specification('absa_env', "absaenv.yml")
    deploy_env.environment_variables={'NLP_ARCHITECT_BE': 'CPU'}


    inference_config = InferenceConfig(environment=deploy_env,
                                   entry_script="score.py")

    deploy_config = AciWebservice.deploy_configuration(cpu_cores=1, 
                                                memory_gb=1,
                                                description='Aspect-Based Sentiment Analysis - Intel')
    print('Initiating deployment')
    deployment = Model.deploy(ws, 'absa-svc', 
                    models=[model], 
                    inference_config=inference_config, 
                    deployment_config=deploy_config, 
                    overwrite=True)

    deployment.wait_for_deployment(show_output=True)
    print('Getting Logs')
    deployment.get_logs()
    print('Done!')

if __name__ == '__main__':
    main()
