const axios = require('axios')
const yaml = require('js-yaml')
const fs = require('fs')
require('process')

const chartRepos = [
  'DeployHubProject/charts',
  'ortelius/ms-compitem-crud',
  'ortelius/ms-dep-pkg-cud',
  'ortelius/ms-dep-pkg-r',
  'ortelius/ms-postgres',
  'ortelius/ms-sbom-export',
  'ortelius/ms-scorecard',
  'ortelius/ms-textfile-crud',
  'ortelius/ms-validate-user'
]

// Helper functions
async function getChartEntries () {
  let sha = ''

  await axios.get('https://api.github.com/repos/DeployHubProject/DeployHub-Pro/commits/main').then(response => {
    sha = response.data.sha
  })

  const url = 'https://raw.githubusercontent.com/DeployHubProject/DeployHub-Pro/' + sha + '/charts/deployhub/Chart.yaml'
  let parts = []
  let latest = ''
  let ver = ''

  await axios.get(url).then(response => {
    const parsedYaml = yaml.load(response.data)
    chartVersion = parsedYaml.version
    parts = chartVersion.split('.')
    ver = parseInt(parts[2]) + 1
    parts[2] = ver.toString()
    chartVersion = parts.join('.')
  })

  const latestChart = []

  for (let i = 0; i < chartRepos.length; i++) {
    await axios.get('https://api.github.com/repos/' + chartRepos[i] + '/commits/gh-pages').then(response => {
      sha = response.data.sha
    })

    const repoUrl = 'https://raw.githubusercontent.com/' + chartRepos[i] + '/' + sha + '/index.yaml'

    await axios.get(repoUrl).then(response => {
      const parsedYaml = yaml.load(response.data)
      const entries = parsedYaml.entries

      Object.keys(entries).forEach(key => {
        latest = null

        Object.entries(entries[key]).forEach(entry => {
          if (latest == null) { latest = entry } else if (latest.created < entry.created) { latest = entry }
        })
        latest = latest[1]

        if (latest.name !== 'dh-jwt' && latest.name !== 'dh-postgres') {
          const dep = {}
          dep.name = latest.name
          dep.version = latest.version

          if (key === 'dh-ms-ui' || key === 'dh-ms-nginx' || key === 'dh-ms-general') {
            key = 'charts'
            dep.repository = 'https://deployhubproject.github.io/' + key + '/'
          } else { dep.repository = 'https://ortelius.github.io/' + key + '/' }

          if (key === 'ms-postgres') { dep.condition = 'global.postgresql.enabled' }

          latestChart.push(dep)
        }

        //    chartEntries[key] = entries[key]
        //    console.log(entries[key]);
      })
    })
  }
  chartEntries = latestChart
  return latestChart
}

function createYamlOutput () {
  const output = yaml.dump({
    apiVersion: 'v2',
    name: 'deployhub',
    description: 'DeployHub Pro',
    home: 'https://www.deployhub.com',
    icon: 'https://deployhubproject.github.io/DeployHub-Pro/deployhub.svg',
    keywords: ['Service Catalog', 'Microservices', 'SBOM'],
    type: 'application',
    version: chartVersion,
    appVersion: '10.0.0',
    dependencies: chartEntries
  }, { noArrayIndent: true })

  fs.readFile('./charts/deployhub/README.md', 'utf8', function (err, data) {
    if (err) {
      return console.log(err)
    }
    const result = data.replace(/DEPLOYHUB_VERSION=\d+\.\d+\.\d+/g, 'DEPLOYHUB_VERSION=' + chartVersion)

    fs.writeFile('./charts/deployhub/README.md', result, 'utf8', function (err) {
      if (err) return console.log(err)
    })
  })

  return output
}
// -----------------

let chartEntries = []
let chartVersion = ''

getChartEntries().then(() => {
  const yamlOutput = createYamlOutput()
  console.log(yamlOutput)
  fs.writeFileSync('./charts/deployhub/Chart.yaml', yamlOutput, 'utf8', (err) => {
    console.log(err)
  })
})
