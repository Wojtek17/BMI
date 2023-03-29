-- Total Population to Vaccinations
SELECT cd.country_continent, ROUND((MAX(vacc.people_vaccinated))/((cd.population)),4)*100 AS vacc_to_population
FROM coviddeaths AS cd
JOIN covidvacc AS vacc ON cd.country_continent=vacc.location AND cd.dat=vacc.dat
WHERE cd.continent IS NOT NULL
GROUP BY cd.country_continent, cd.population
HAVING (MAX(vacc.people_vaccinated))/((cd.population))>0
ORDER BY (MAX(vacc.people_vaccinated))/((cd.population)) DESC
