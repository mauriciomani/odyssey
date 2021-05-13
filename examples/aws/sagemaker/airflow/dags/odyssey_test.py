from datetime import datetime
from airflow import DAG
from odyssey_operators import OdysseySagemakerTrain
from odyssey_operators import OdysseySagemakerBatchTransform
from odyssey_operators import OdysseySagemakerServe


# It is mandatory to include this in dags folder
# Have file in odyssey_operators in the plugins folder

dag = DAG("odyssey_test",
          description="Simple odyssey operator",
          schedule_interval="* * * * *",
          start_date=datetime(2021, 1, 1),
          catchup=False)


sagemaker_train = OdysseySagemakerTrain(role="arn:aws:iam::__num__:role/sagemaker_role",
                                        image_name="airflow_image",
                                        input_path="s3://testapp/airflow_test_sagemaker/input/data/training/iris.data",
                                        model_path="s3://testapp/airflow_test_sagemaker/model/",
                                        task_id='odyssey_train',
                                        dag=dag)

sagemaker_serve = OdysseySagemakerServe(role="arn:aws:iam::__num__:role/sagemaker_role",
                                        image_name="airflow_image",
                                        endpoint_name="airflow-test",
                                        bucket="testapp",
                                        odyssey_app="airflow_test_sagemaker",
                                        task_id="odyssey_serve",
                                        dag=dag)

sagemaker_batch = OdysseySagemakerBatchTransform(role="arn:aws:iam::__num__:role/sagemaker_role",
                                                 image_name="airflow_image",
                                                 output_path="s3://testapp/airflow_test_sagemaker/output/",
                                                 input_path="s3://testapp/airflow_test_sagemaker/input/data/iris.csv",
                                                 bucket="testapp",
                                                 odyssey_app="airflow_test_sagemaker",
                                                 task_id="odyssey_batch_transform",
                                                 dag=dag)

# Both cannot be used
#sagemaker_train >> sagemaker_serve
#sagemaker_train >> sagemaker_batch
