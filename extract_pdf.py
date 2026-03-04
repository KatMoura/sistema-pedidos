import PyPDF2
path = r"c:\Users\Diego\Downloads\ATIVIDADE_FINAL__Refatoração_Arquitetural_para_Microserviços-80a864467b3f48d29_UauxCR5.pdf"
reader = PyPDF2.PdfReader(path)
for i, page in enumerate(reader.pages):
    print("--- page", i+1, "---")
    print(page.extract_text())
