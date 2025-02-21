from langchain.prompts import PromptTemplate

prompt_template_personal_summary = PromptTemplate(
    input_variables=["name", "company", "position", "country", "google_results"],
    template=(
        "Create an engaging summary about {name} {position} from {company} based on {country} that helps understand the person professionally "
        "to facilitate meaningful conversations.\n\n"
        "Extract and summarize the key details concisely. Aim for 120 words or more if possible, but if the available information is limited, "
        "provide whatever is found—even if it’s just a single sentence. Do not omit details solely because they do not reach 120 words.\n\n"
        "Include the following aspects in the summary:\n"
        "- Their current work and interests\n"
        "- Professional background and expertise\n"
        "- Any passion projects or focus areas\n"
        "- Notable achievements or contributions\n"
        "- Industry perspectives or thought leadership\n"
        "- Any interesting professional activities (speaking, writing, research)\n"
        "- Areas they seem passionate about\n\n"
        "- Educational Background and more\n\n"
        "IMPORTANT - Exclude:\n"
        "- Personal contact infromations like , Email address , Phone Number like these private data\n\n"
        "Be flexible with role titles - focus on their domain and actual work rather than exact position matches.\n"
        "If you find partial information, include it as long as it helps build a conversation with infromation that can get from given data. do not make assumptions or add information beyond what is explicitly found in the search results.\n"
        "IMPORTANT - Respond 'Geronimo unable to provide information about {name} at {company}' only if:\n"
        "- 1. Theres no any information about {name} in {company} \n"
        "- 2. The found information is about a completely different person in an unrelated field\n\n"
        "- If the data is there but not enough to create a summary, provide as much information as possible.\n"
        "Dont Just say 'No information found' if there is some information available.\n\n"
        "Refer the Google Search Results carefully to extract the infromation about the person: \n"
        "Google Search Results include following structure:\n"
        "- Title: The title of the search result , Can get overall idea about result get information from there also\n"
        "- Link: The URL of the search result\n"
        "- Snippet: The snippet of the search result , Can use to when generating response if this discribe correct person\n"
        "- Content: This is the web scraped content of the result and it can be an error massage also, ignore this if it is an error\n"
        "- Possition: The posisition that result placed in the search results, Prioritize top results but verify accuracy\n"
        "Generate response reader friendly way"
        "Google Search Results: {google_results}\n\n"
        "Summary: "
    ),
)


prompt_template_social_links = PromptTemplate(
    input_variables=["name", "company", "position", "country", "google_results"],
    template=(
        "Find the most accurate social media and professional profile links for {name}, who works at {company} as {position} in {country}. "
        "\n\n"
        "Guidelines for link verification:\n"
        "- Verify profile ownership by matching name, company, and professional background\n"
        "- Select only ONE most relevant and active link per platform\n"
        "- Prioritize profiles that show current role or company association\n"
        "- For similar names, use company and role information to confirm identity\n"
        "\n"
        "Look for these types of profiles:\n"
        "1. Professional Networks: LinkedIn, Xing, etc.\n"
        "2. Tech Profiles: GitHub, GitLab, Stack Overflow\n"
        "3. Social Media: Twitter,Facebook , Instragram, Mastodon ect \n"
        "4. Content Platforms: Medium, blog sites, speaking profiles\n"
        "5. Professional Directories: Company profile page of the person in {company}, conference speaker profiles\n"
        "6. Educational Profiles: Google Scholer profile, ResearchGate ect. \n"
        "7. If it includes a person's portfolio or personal website, mention it only if it's correct."
        "Try to find the atleast correct LinkedIn profile of the person from the given results\n"
        "\n"
        "Exclude:\n"
        "- Company or organization main pages\n"
        "- News articles or press releases\n"
        "- Project repositories or team pages\n"
        "- Duplicate profiles on the same platform\n"
        "- Inactive or outdated profiles\n"
        "\n"
        "Output the result as a JSON array each item enclosed with curly brackets in the following format:\n\n"
        '  -platform": "platform_name", -url": "URL",\n'
        "Ensure there is one object for each social media link. If no valid links are found, return an empty array. but try to identify atleast one platform link\n\n"
        "IMPORTANT - Do not generate any URL by using person name, just give the URL if it is found in the google search results else Do not hallucinate URL \n\n"
        "\n"
        "Google Search Results with URL: {google_results}\n"
        "\n"
        "JSON Array Output:"
    ),
)

prompt_template_company_summary = PromptTemplate(
    input_variables=["company", "country", "google_results"],
    template=(
        "Create a detailed company summary for {company} based in {country} using the provided search results. Each search result contains: "
        "title, link, snippet, and content sections.\n\n"
        "First, analyze the search results for relevant company information:\n"
        "- Check company name matches in titles and content\n"
        "- Look for official company websites or verified business listings\n"
        "- Focus on business descriptions from credible sources\n\n"
        "If ANY valid company information is found, create a comprehensive summary (around 200 words) covering:\n"
        "1. Company's primary business activities and focus\n"
        "2. Key services and products offered\n"
        "3. Geographical presence and market coverage\n"
        "4. Notable projects, achievements, or unique aspects\n"
        "5. Industry expertise and target sectors\n\n"
        "Important Guidelines:\n"
        "- Use information from multiple search result sections (title, snippet, content) to verify details\n"
        "- Create a flowing narrative that connects available information\n"
        "- Include specific examples when available\n"
        "- If some aspects are unknown, focus on the information that is available\n"
        "- Even minimal but verified information about the company should be included\n"
        "- Give detail what you found from search results about the company. do not be strictly on word count\n"
        "- Give response based on the given data and do not hallucinate the data\n"
        "- Ignore the Error massages that gives in search results when doing web scraping. do not inlcude about them in the response\n\n"
        "If multiple companies are found with the same name:\n"
        "First try to find the company that is given in the query and provide the details about that company\n"
        "You can use person name and position to identify the correct company\n"
        "if not , Start with: 'Geronimo Found multiple companies named {company}. Here are the details:'\n"
        "Then provide a flowing paragraph about each company, focusing on their core business, key offerings, and distinguishing "
        "characteristics. Keep the total response within 250 words and maintain clear separation between companies without using "
        "bullets, numbers, or special formatting.\n\n"
        "ONLY return 'Geronimo unable to find valid information about {company}' if:\n"
        "- None of the search results mention the company's business activities\n"
        "- All search results are about a different company\n\n"
        "Search Results: {google_results}\n\n"
        "Summary:"
    ),
)

prompt_template_competitors = PromptTemplate(
    input_variables=["company", "google_results"],
    template=(
        "Analyze the following Google Search results to identify competitor companies for {company}. "
        "Extract and return only the names of valid competitor companies that are directly mentioned in the provided search results, "
        "ensuring they are distinct entities in the same domain/industry as {company}. "
        "Strictly exclude product names, services, or unrelated entities. "
        "Provide a list of 3 to 5 valid competitor company names as a comma-separated list, sorted alphabetically. "
        "Do not fabricate or hallucinate any competitors. "
        "If no valid competitor names can be identified from the results, return an empty response without any text.\n\n"
        "Google Search Results: {google_results}\n\n"
        "Competitor Company Names (comma-separated):"
    ),
)


prompt_template_news = PromptTemplate(
    input_variables=["company", "google_results", "date"],
    template=(
        "Based on the following Google Search results for {company}'s recent news, provide a JSON-formatted summary of the top 3 to 5 most relevant news articles from only the last 12 months. reffer today date that mention in prompt"
        "If it include past big News then mention them also."
        "Only focus on the articles that are related to the company, don't mention the articles with similar names or unrelated to the company. "
        "Focus on articles related to the company's financial performance, major partnerships, executive changes, or significant industry developments. "
        "Do not generate news articles, just give the news according to the given data with reference to the URL. "
        "For each article, include the following details:\n"
        "- 'title': A clear, detailed, and accurate title that gives a precise idea of the news.\n"
        "- 'url': The full, complete, and correct link to the news article.\n"
        "- 'description': A concise but informative summary of the news content, not exceeding 100 words.\n"
        "If no valid news articles are found, return an empty response without any text.'\n\n"
        "Today's Date: {date}\n\n"
        "Google Search Results: {google_results}\n\n"
        "Company News Json:"
    ),
)


prompt_template_summarization = PromptTemplate(
    input_variables=["query", "chunk"],
    template=(
        "You are a summarization assistant tasked with extracting only the most relevant information from web-scraped content by clearing out any unwanted details. "
        "based on the given query. The query primarily pertains to a person or a company, and the provided content chunk "
        "contains potentially useful details. Your goal is to generate a clear, concise summary that directly answers the query "
        "while eliminating any extraneous or irrelevant details.\n\n"
        "Guidelines:\n"
        "- Extract only information that is directly relevant to the query.\n"
        "- Ensure the summary is precise and avoids unnecessary details or assumptions.\n"
        "- If the available content is insufficient to generate a meaningful summary, provide as much relevant information as possible.\n"
        "- if can't find any information in given content, do not hallucinate the data'\n"
        "- If no relevant information is found, return: 'No Content Available to Summarize.'\n"
        "- The content originates from web scraping, so structure the summary accordingly.\n\n"
        "Query: {query}\n\n"
        "Web-Scraped Content: {chunk}\n\n"
        "Summary:"
    ),
)
