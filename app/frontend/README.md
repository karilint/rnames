Wizard is an experimental implementation of [stepwise data entry](https://rnames-staging.it.helsinki.fi/rnames/help/instruction) in React.

## Running wizard in production environment

```sh
~/rnames$ cd app/frontend
~/rnames/app/frontend$ npm install && npm run build
```

## Running wizard in development environment

```sh
~/rnames$ cd app/frontend
~/rnames/app/frontend$ npm install && npm run dev
```

Development environment enables live reloading and using Redux devtools (available as extension on Google Chrome).

After starting the wizard, RNames dev environment is initialized using the command

```sh
~/rnames$ docker-compose up -d --build
```

For more information about running the RNames development environment visit [this](https://github.com/karilint/rnames/blob/master/docs/dev_environment.md) page.

## Running tests

```sh
~/rnames/app/frontend$ npm test
```

Running tests in [watch](https://jestjs.io/docs/cli#--watch) mode

```sh
~/rnames/app/frontend$ npm run test:watch
```

Running tests with coverage report (full coverage report is located in the folder `~/rnames/app/frontend/coverage`)

```sh
~/rnames/app/frontend$ npm run test:coverage
```

---

Combining React + Django [reference](https://github.com/techwithtim/Music-Controller-Web-App-Tutorial/tree/main/Tutorial%201%20-%204/frontend)
