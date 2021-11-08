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

---

Combining React + Django [reference](https://github.com/techwithtim/Music-Controller-Web-App-Tutorial/tree/main/Tutorial%201%20-%204/frontend)
