from typing import TypedDict, List, Optional, NotRequired, Dict, Any
from enum import Enum
from dataclasses import dataclass, field


def get_state_file() -> str:
    return os.getenv("STATE_FILE", "jaysons/job_state.json")


class CompanyObject(TypedDict, total=False):
    id: str
    name: str
    domain: str
    industry: str
    country: str
    country_code: str
    employee_count: int
    logo: str
    num_jobs: int
    num_technologies: int
    possible_domains: List[str]
    url: str
    industry_id: int
    linkedin_url: str
    num_jobs_last_30_days: int
    num_jobs_found: Optional[int]
    yc_batch: Optional[Any]
    apollo_id: Optional[Any]
    linkedin_id: str
    url_source: Optional[str]
    is_recruiting_agency: bool
    founded_year: Optional[int]
    annual_revenue_usd: Optional[float]
    annual_revenue_usd_readable: Optional[str]
    total_funding_usd: Optional[float]
    last_funding_round_date: Optional[str]
    last_funding_round_amount_readable: Optional[str]
    employee_count_range: str
    long_description: str
    seo_description: str
    city: str
    postal_code: Optional[str]
    company_keywords: List[str]
    alexa_ranking: Optional[int]
    publicly_traded_symbol: Optional[str]
    publicly_traded_exchange: Optional[str]
    investors: List[Any]
    funding_stage: Optional[str]
    has_blurred_data: bool
    technology_slugs: List[str]
    technology_names: List[str]

class Location(TypedDict, total=False):
    id: int
    name: str
    type: str
    feature_code: str
    country_code: str
    admin1_name: str
    admin1_code: str
    admin2_name: str
    admin2_code: str
    continent: str
    latitude: float
    longitude: float
    city: str
    address: Optional[str]
    postal_code: Optional[str]
    state: str
    state_code: str
    display_name: str
    country_name: str

class JobRecord(TypedDict, total=False):
    id: int
    job_title: str
    url: str
    date_posted: str
    has_blurred_data: bool
    company: str
    final_url: str
    source_url: str
    location: str
    short_location: str
    long_location: str
    state_code: str
    latitude: float
    longitude: float
    postal_code: Optional[str]
    remote: bool
    hybrid: bool
    salary_string: Optional[str]
    min_annual_salary: Optional[float]
    min_annual_salary_usd: Optional[float]
    max_annual_salary: Optional[float]
    max_annual_salary_usd: Optional[float]
    avg_annual_salary_usd: Optional[float]
    salary_currency: Optional[str]
    countries: List[str]
    country: str
    country_codes: List[str]
    country_code: str
    cities: List[str]
    continents: List[str]
    seniority: str
    discovered_at: str
    company_domain: str
    hiring_team: List[Any]
    reposted: bool
    date_reposted: Optional[str]
    employment_statuses: List[str]
    easy_apply: Optional[bool]
    technology_slugs: List[str]
    description: str
    company_object: CompanyObject
    locations: List[Location]
    normalized_title: str
    manager_roles: List[Any]
    matching_phrases: List[str]
    matching_words: List[str]

    # Custom extensions:
    filter_reason: Optional[str]
