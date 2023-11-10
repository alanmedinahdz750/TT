import openai

openai.api_key = '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'

response = openai.Completion.create(
    model = 'text-davinci-003',
    prompt = 'Decide si un tweet es positivo, nutral o negativo \
    \n\n Tweet: Odie la pelicula de ms Marvel\"\nSentimen: ',
    temperature = 0,
    max_tokens = 60,
    top_p = 1,
    frequency_penalty = 0.5,
    presence_penalty = 0
)

print(response.choices[0].text)