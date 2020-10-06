# covid19-case-counts

Source code for Covid-19 town-by-town case counts website. The website linked contains a previous version of the webapp.

NOTE: Contributor "tagproman" is an old account of mine and I have since transitioned to "prathik2001." 

**Using The API**

To retrieve information about all cities/towns/zip codes in a specific state: covidcitycounts.com/api/cases?state=(state)

Replace (state) with "florida", "massachusetts", or "arizona" as necessary. Ensure that the state name is in all lowercase characters.

*Note*: ensure when passing in the parameters below that the county and city name capitalizes the first letter of each word in the argument. Do not replace spaces in a county or city name with an underscore or other character, simply type in the space.

To retrieve information about a specific county, zip code, or city: covidcitycounts.com/api/cases?state=(state)&county=(county)
covidcitycounts.com/api/cases?state=(state)&city=(city)
covidcitycounts.com/api/cases?state=(state)&zip=(zip)

The state argument is required for all API calls. If multiple calls out of city, county, and zip code are made, the API will default to giving information about the city, or the zip code if the city was not one of the arguments.

To pass multiple arguments for a single parameter:
covidcitycounts.com/api/cases?state=(state)&city=(city1),(city2),(city3)
Repeated for however many arguments are necessary. 

*Note*: it is not possible to select multiple states in this manner as each state uses a different data set.