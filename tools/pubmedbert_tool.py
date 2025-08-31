from transformers import AutoTokenizer, AutoModelForMaskedLM, pipeline

def pubmedbert_summarize(text):
    """
    Use PubMedBERT to extract biomedical knowledge or summarize a protein/gene/compound.
    """
    tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")
    model = AutoModelForMaskedLM.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext")
    fill_mask = pipeline("fill-mask", model=model, tokenizer=tokenizer)
    prompt = f"{text} is associated with [MASK]."
    results = fill_mask(prompt)
    return [f"{r['sequence']} (score: {r['score']:.3f})" for r in results]
