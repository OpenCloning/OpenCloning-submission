
function sanitizeString(str) {
    return str
        .trim()
        .replace(/[\r\n]+/g, ' ')
        .replace(/\s+/g, ' ')
}

async function makeHtmlTable(plasmids) {
    const table = document.createElement('table')
    table.classList.add('table')
    const headerRow = document.createElement('tr')
    const tableHeaders = ['well', 'name', 'addgene_id', 'resistance']
    tableHeaders.forEach(header => {
        const th = document.createElement('th')
        th.innerText = header
        headerRow.appendChild(th)
    })
    table.appendChild(headerRow)
    plasmids.forEach(plasmid => {
        const row = document.createElement('tr')
        const well = document.createElement('td')
        well.innerText = plasmid.well
        const name = document.createElement('td')
        name.innerText = plasmid.name
        const addgene_id = document.createElement('td')
        addgene_id.innerText = plasmid.addgene_id
        const resistance = document.createElement('td')
        resistance.innerText = plasmid.resistance
        row.appendChild(well)
        row.appendChild(name)
        row.appendChild(addgene_id)
        row.appendChild(resistance)
        table.appendChild(row)
    })
    return table;
}
async function scrape() {
    // Get the scraped content using the backend
    const addgeneUrl = document.getElementById('addgene-url').value
    const response = await fetch(`/scrape_addgene?url=${addgeneUrl}`)
    if (!response.ok) {
        const responseJson = await response.json()
        throw new Error(responseJson.detail)
    }
    const htmlContent = await response.text()

    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlContent, 'text/html');
    // the last element (sometimes there is a table with only headers on top)
    const elements = doc.querySelectorAll('#kit-contents table.kit-inventory-table')
    const kitTable = elements[elements.length - 1]

    // Check that the headers of the table are Well, Plasmid and Resistance
    const headers = kitTable.querySelectorAll('thead th')
    if (headers.length !== 3) {
        alert('The html document does not have the expected structure')
        return
    }
    const headerText = Array.from(headers).map(header => header.innerText.trim())
    if (headerText[0] !== 'Well' || headerText[1] !== 'Plasmid' || headerText[2] !== 'Resistance') {
        alert('The table does not have the expected headers')
        return
    }

    // Get the plasmid info
    const plasmids = Array.from(kitTable.querySelectorAll('tbody tr')).map(row => {
        const cells = row.querySelectorAll('td')
        const idHref = cells[1].querySelector('a').href.split('/')
        // For now, it seems that ids are /id/ (they have trailing slash)
        // But it is better to be safe and pop twice, since first pop will
        // be false if there is no trailing slash
        const addgene_id = idHref.pop() || idHref.pop()
        return {
            well: sanitizeString(cells[0].innerText),
            name: sanitizeString(cells[1].innerText),
            addgene_id,
            resistance: sanitizeString(cells[2].innerText),
        }
    })
    // Make an html table
    const table = await makeHtmlTable(plasmids)
    document.getElementById('table-result').appendChild(table)

    // Allow the user to download the table as tsv
    const downloadButton = document.getElementById('download-button')
    downloadButton.onclick = () => {
        let tsv = 'name\taddgene_id\tcategory\tresistance\twell\tdescription\n'
        tsv += plasmids.map(plasmid => {
            const { well, name, addgene_id, resistance } = plasmid
            return [name, addgene_id, '', resistance, well, ''].join('\t')
        }).join('\n')
        const blob = new Blob([tsv], {
            type: 'text/tsv'
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'plasmids.tsv'
        a.click()
        URL.revokeObjectURL(url)
    }
}
async function submitFunction(e) {
    e.preventDefault();
    const loading = document.getElementById('loading')
    const downloadButton = document.getElementById('download-button')
    const errorAlert = document.querySelector('.alert-danger')
    document.getElementById('table-result').innerHTML = ''
    try {
        errorAlert.hidden = true
        loading.hidden = false
        await scrape()
        downloadButton.hidden = false
    } catch (e) {
        errorAlert.hidden = false
        errorAlert.innerText = e
        downloadButton.hidden = true
    }
    finally {
        loading.hidden = true
    }
}

window.onload = () => {
    document
        .getElementById("main-form")
        .addEventListener("submit", submitFunction);
};