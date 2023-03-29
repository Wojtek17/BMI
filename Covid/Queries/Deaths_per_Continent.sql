--Deaths total number per continent
SELECT continent, SUM(new_deaths)
FROM coviddeaths
WHERE continent IS NOT NULL
GROUP BY continent
HAVING SUM(new_deaths) >0
ORDER BY SUM(new_deaths) DESC
