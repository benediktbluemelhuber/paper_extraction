from langchain_community.chat_models import ChatOpenAI
from pypdf import PdfReader
import pandas as pd
import re
import replicate
from langchain.prompts import PromptTemplate
from tornado.websocket import WebSocketClosedError
from langchain_core.output_parsers import JsonOutputParser
import json
from langchain_core.pydantic_v1 import BaseModel, Field


# Extract Information from PDF file
def get_pdf_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


class AcademicPaper(BaseModel):
    Title: str = Field(description="The title of the paper.")
    Authors: str = Field(description="List of authors of the paper.")
    Date_Published: str = Field(
        description="Date when the paper was published or submitted."
    )
    Link: str = Field(description="Web link to the paper.")
    Comments: str = Field(
        description="Comments about the paper, such as publication status or venue."
    )
    TLDR: str = Field(description="A one or two line summary of the paper.")
    Relevance: str = Field(
        description="A score between 1 and 5 stating how relevant this paper is to your work."
    )
    Tags: str = Field(
        description="Research topic tags, conference names, or other useful groupings."
    )
    Paper_Summary: str = Field(
        description="Summary of the paper including its hypothesis and what was done."
    )
    Issues_Addressed_by_the_Paper: str = Field(
        description="Description of the issues that the paper addresses."
    )
    Problem_Setting: str = Field(
        description="The problem setting of the paper, including specifics like the environment, rewards, and evaluation settings."
    )
    Methodology: str = Field(
        description="Description of the methods used to approach the problem."
    )
    Assumptions: str = Field(
        description="Assumptions made in the paper and their validity."
    )
    Prominent_Formulas: str = Field(
        description="Important formulas used or introduced in the paper."
    )
    Results: str = Field(
        description="Theoretical or empirical results, including main graphs and tables."
    )
    Limitations: str = Field(
        description="Limitations of the work as mentioned by the authors or observed by the reader."
    )
    Confusing_Aspects: str = Field(
        description="Aspects of the paper that are confusing or need better explanations."
    )
    Authors_Conclusions: str = Field(
        description="The conclusions drawn by the authors about their results."
    )
    My_Conclusion: str = Field(description="Personal conclusions about the paper.")
    Rating: str = Field(description="A rating of the paper (e.g., Fine, Good, Great).")
    Possible_Future_Work: str = Field(
        description="Suggestions for potential future research or improvements based on the paper."
    )
    Relation_to_Own_Work: str = Field(
        description="How the paper relates to your own work, if applicable."
    )
    Learn_from_Approach: str = Field(
        description="What can be learned from the paper's approach and methodology."
    )
    How_Are_We_Different: str = Field(
        description="Differences between your approach and the paper's approach."
    )
    Extra_Info: str = Field(
        description="Any extra information such as cited references, related papers, source code links, blog posts, or other relevant links."
    )


# Function to extract data from text
def extracted_data(pages_data):
    template = """You are an expert in extracting relevant information from a paper.
        
        Extract all the following values given in {format_instructions} from the paper with the following text:
    
        '''{pages}'''. 
        
        Do not come up with other values than the ones given to you. Think really hard and in a methodical way to only extract to relevant information.
    """

    parser = JsonOutputParser(pydantic_object=AcademicPaper)

    prompt = PromptTemplate(
        input_variables=["pages"],
        template=template,
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    model = ChatOpenAI(model="gpt-4-1106-preview", temperature=0.1)

    chain = prompt | model | parser

    full_response = chain.invoke({"pages": pages_data})

    print(full_response)
    return full_response


# iterate over files in
# that user uploaded PDF files, one by one
def create_paper_review_df(user_pdf_list):
    df = pd.DataFrame(
        {
            "Title": pd.Series(dtype="str"),
            "Authors": pd.Series(dtype="str"),
            "Date_Published": pd.Series(dtype="str"),
            "Link": pd.Series(dtype="str"),
            "Comments": pd.Series(dtype="str"),
            "TLDR": pd.Series(dtype="str"),
            "Relevance": pd.Series(dtype="int"),
            "Tags": pd.Series(dtype="str"),
            "Paper_Summary": pd.Series(dtype="str"),
            "Issues_Addressed_by_the_Paper": pd.Series(dtype="str"),
            "Problem_Setting": pd.Series(dtype="str"),
            "Methodology": pd.Series(dtype="str"),
            "Assumptions": pd.Series(dtype="str"),
            "Prominent_Formulas": pd.Series(dtype="str"),
            "Results": pd.Series(dtype="str"),
            "Limitations": pd.Series(dtype="str"),
            "Confusing_Aspects": pd.Series(dtype="str"),
            "Authors_Conclusions": pd.Series(dtype="str"),
            "My_Conclusion": pd.Series(dtype="str"),
            "Rating": pd.Series(dtype="str"),
            "Possible_Future_Work": pd.Series(dtype="str"),
            "Relation_to_Own_Work": pd.Series(dtype="str"),
            "Learn_from_Approach": pd.Series(dtype="str"),
            "How_Are_We_Different": pd.Series(dtype="str"),
            "Extra_Info": pd.Series(dtype="str"),
        }
    )

    for filename in user_pdf_list:
        print(filename)
        raw_data = get_pdf_text(filename)
        # print("extracted raw data")

        llm_extracted_data = extracted_data(raw_data)
        print("llm extracted data")
        print(llm_extracted_data)
        # Adding items to our list - Adding data & its metadata

        data_dict = llm_extracted_data

        try:
            df_dictionary = pd.DataFrame([data_dict])
            df = pd.concat([df, df_dictionary], ignore_index=True)
            print("********************DONE***************")
        except WebSocketClosedError as e:
            raise e
        # df=df.append(save_to_dataframe(llm_extracted_data), ignore_index=True)

    df.head()
    return df
