-- Global numbers
SELECT SUM(new_cases) AS total_cases, SUM(new_deaths) AS total_deaths, ROUND(CAST(SUM(new_deaths)AS DECIMAL)/SUM(new_cases),4)*100 AS death_percentage
FROM coviddeaths
WHERE continent IS NOT NULL
