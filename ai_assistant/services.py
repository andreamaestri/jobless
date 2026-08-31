import logging

from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)

CV_MAX_CHARS = 30000
JOB_DESCRIPTION_MAX_CHARS = 12000
EXTRA_INSTRUCTIONS_MAX_CHARS = 1000

SYSTEM_PROMPT = """You are an expert technical recruiter and career coach with over 15 years of experience hiring for technology roles.

You always follow these rules:
- Ground every point in evidence: quote or paraphrase specifics from the CV or the job description.
- Be candid but constructive. Never invent experience, skills, employers, dates or metrics that are not in the CV.
- Prioritise ruthlessly: lead with what matters most for getting this specific role.
- Write in clean Markdown: ## section headings, short paragraphs, bullet lists, **bold** for key terms.
- Keep a professional, encouraging tone. No emojis."""

FEEDBACK_INSTRUCTIONS = """Analyse the candidate's CV against the target role below.

Produce a Markdown document with exactly these sections:

## Fit summary
2-3 sentences giving an honest verdict, then a final line: **Fit rating:** Strong / Moderate / Stretch.

## What works
3-5 bullets mapping the candidate's strongest relevant experience to this role's requirements.

## Gaps and risks
3-5 bullets of the biggest concerns. Distinguish between "missing from the CV but maybe held by the candidate" and "likely genuinely missing". Note requirements that appear unsatisfiable.

## Skill alignment
Go through the role's listed skills. For each important one output a bullet:
`- **<skill>** (<required/preferred/nice to have>) — Met | Partial | Missing — <one short sentence of evidence from the CV>`

## Top improvements
The 5 highest-impact changes to the CV for this application, ordered by impact. For each:
- **<change title>** — why it matters for THIS role (1-2 sentences), then an example rewrite where relevant:
  - Before: <quoted line or summary of the current CV text>
  - After: <concrete replacement wording>

## Interview prep
2-4 questions an interviewer for this role would likely ask to probe the gaps above, each with one sentence of guidance on how to answer using the candidate's real experience.

Be specific to this job description everywhere. Do not give generic advice."""

COVER_LETTER_INSTRUCTIONS = """Write a complete cover letter for the candidate, applying to the target role below.

Requirements:
- 250-350 words unless extra instructions say otherwise.
- Open with a genuine hook that references something concrete about the company, product or role from the job description. Avoid cliches like "I am writing to apply for".
- Body: map the candidate's 2-4 strongest, most relevant achievements from their CV directly onto the top requirements of the role. Use specifics (technologies, scope, outcomes) from the CV.
- If the CV has an obvious gap against the role, address it briefly and confidently in one sentence - do not dwell on it.
- Close with a confident call to action.
- Sign off as "{candidate_name}".
- Format: plain prose paragraphs only - no Markdown headings, bullet lists, bold or other formatting. It must look right pasted into an email.
- Output ONLY the letter itself, no preamble or meta commentary."""

TONES = {
    'professional': "Tone: professional and measured.",
    'warm': "Tone: warm and personable, while staying credible.",
    'concise': "Tone: direct and concise. Prefer short sentences and cut every filler word.",
}


def get_model(task=None):
    if task == 'feedback':
        return getattr(settings, 'GEMINI_MODEL_FEEDBACK', None) or settings.GEMINI_MODEL
    if task == 'cover_letter':
        return getattr(settings, 'GEMINI_MODEL_COVER_LETTER', None) or settings.GEMINI_MODEL
    return settings.GEMINI_MODEL


def _client():
    return OpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=settings.GEMINI_API_KEY,
        timeout=90,
        max_retries=1,
    )


def clean_extra_instructions(text):
    return (text or "").strip()[:EXTRA_INSTRUCTIONS_MAX_CHARS]


def build_job_context(job):
    lines = [
        f"Role title: {job.title}",
        f"Company: {job.company}",
        f"Location: {job.location}",
    ]
    if job.salary_range:
        lines.append(f"Salary range: {job.salary_range}")
    lines.append("")
    lines.append("Job description:")
    description = job.description
    if len(description) > JOB_DESCRIPTION_MAX_CHARS:
        description = description[:JOB_DESCRIPTION_MAX_CHARS] + "\n[...truncated...]"
    lines.append(description)

    skills = []
    for js in job.job_skills.select_related('skill').all():
        skills.append(
            f"- {js.skill.label} ({js.get_proficiency_display()})"
        )
    if skills:
        lines.append("")
        lines.append("Skills listed for this role:")
        lines.extend(skills)
    return "\n".join(lines)


def feedback_messages(cv_text, job, extra_instructions=""):
    user_parts = []
    if job is not None:
        user_parts.append("## Target role\n" + build_job_context(job))
    else:
        user_parts.append(
            "## Target role\nNo specific job was selected. Review the CV for general "
            "strength and market-readiness for senior tech roles, and say so explicitly "
            "instead of assuming a particular vacancy."
        )
    user_parts.append("## Candidate CV\n" + cv_text)
    user_parts.append("## Your task\n" + FEEDBACK_INSTRUCTIONS)
    if extra_instructions:
        user_parts.append("## Candidate's focus requests\n" + extra_instructions)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "\n\n".join(user_parts)},
    ]


def cover_letter_messages(cv_text, job, tone='professional', extra_instructions="", candidate_name=""):
    name = (candidate_name or "").strip() or "[Your Name]"
    instructions = COVER_LETTER_INSTRUCTIONS.replace("{candidate_name}", name)
    if tone in TONES:
        instructions += "\n" + TONES[tone]
    user_parts = [
        "## Target role\n" + build_job_context(job),
        "## Candidate CV\n" + cv_text,
        "## Your task\n" + instructions,
    ]
    if extra_instructions:
        user_parts.append("## Candidate's extra instructions\n" + extra_instructions)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "\n\n".join(user_parts)},
    ]


def stream_completion(messages, task=None):
    client = _client()
    model = get_model(task)
    logger.info("AI completion started model=%s task=%s", model, task)
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        stream=True,
        temperature=0.6,
    )
    for update in response:
        delta = update.choices[0].delta.content if update.choices else None
        if delta:
            yield delta
