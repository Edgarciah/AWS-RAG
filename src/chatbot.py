import os
import boto3
import json
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Set up the default session for boto3 using the profile specified in the .env file
boto3.setup_default_session(profile_name=os.getenv('profile_name'))

# Instantiate the Bedrock client and the Bedrock Agent Runtime client 
bedrock = boto3.client('bedrock-runtime', os.getenv('bedrock_region'))
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', os.getenv('bedrock_region'))

# Retrieve the knowledge base ID from the .env file
knowledge_base_id = os.getenv('knowledge_base_id')

def get_contexts(query, knowledge_base_id, num_results=5):
    """
    Retrieve contexts for a given query from a specified knowledge base.
    
    :param query: Natural language query to be processed.
    :param knowledge_base_id: ID of the knowledge base from which to retrieve contexts.
    :param num_results: Number of results to retrieve from the knowledge base (default is 5).
    :return: List of contexts related to the query.
    """
    # Retrieve contexts for the query from the knowledge base
    results = bedrock_agent_runtime.retrieve(
        retrievalQuery={
            'text': query
        },
        knowledgeBaseId=knowledge_base_id,
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': num_results
            }
        }
    )
    
    # Extract and return the text content from the retrieval results
    contexts = [result['content']['text'] for result in results['retrievalResults']]
    return contexts

def answer_query(user_input):
    """
    Answer a user's query by retrieving relevant contexts from the knowledge base and generating a response using the LLM.
    
    :param user_input: Natural language question from the user.
    :return: Generated response to the user's question based on retrieved contexts.
    """
    # Retrieve contexts for the user's query
    user_query = user_input
    user_contexts = get_contexts(user_query, knowledge_base_id)

    # Set up the prompt template for the LLM
    prompt_template = """
    You are an assistant with a broad domain in Amazon Web Services. Your objective is to answer the questions directly from the user with the context provided. If you don't have an answer, respond with "I don't have enough context."
    
    Here is the context:
    <context>
    {context_str}
    </context>
    
    According to the context, answer the user's question:
    <question>
    {query_str}
    </question>
    """

    # Format the prompt with the retrieved contexts and the user's query
    formatted_prompt = prompt_template.format(context_str=user_contexts, query_str=user_query)

    # Set up the parameters for the model, preparing for inference
    prompt = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 2000,
        "temperature": 0.8,
        "top_p": 0.5,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": formatted_prompt
                    }
                ]
            }
        ]
    }
    
    # Convert the prompt to a JSON string
    json_prompt = json.dumps(prompt)    

    # Invoke the model by passing the formatted prompt
    response = bedrock.invoke_model(body=json_prompt, modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                                    accept="application/json", contentType="application/json")
    
    # Parse the response from Claude
    response_body = json.loads(response.get('body').read())
    final_response = response_body['content'][0]['text']
    
    # Return the final response to the user
    return final_response

