--Highest infection rate
SELECT country_continent, MAX(total_cases), ROUND(MAX(total_cases/population),4)*100 AS infection_rate
FROM coviddeaths
GROUP BY country_continent
HAVING MAX(total_cases/population) >0
ORDER BY (MAX(total_cases/population)) DESC
