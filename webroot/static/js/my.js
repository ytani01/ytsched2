/**
 *   (c) 2021 Yoichi Tanibayashi
 */

/**
 *
 */
const doPost = (path, data) => {
    console.log(`doPost()`);

    const form = document.createElement("form");
    form.setAttribute("action", path);
    form.setAttribute("method", "POST");
    form.style.display = "none";
    document.body.appendChild(form);

    if (data !== undefined) {
        for (let param in data) {
            const input = document.createElement("input");
            input.setAttribute("type", "hidden");
            input.setAttribute("name", param);
            input.setAttribute("value", data[param]);
            form.appendChild(input);
        }
    }
    form.submit();
};

/**
 *
 */
const doPostDate = (path, date, days = 0) => {
    let d1 = new Date(date);
    d1.setDate(d1.getDate() + days);
    d1_str = d1.toISOString().replace(/T.*$/, '');
    console.log(`date=${date}, d1_str=${d1_str}`);

    doPost(path, {date: d1_str});
};

/**
 *
 */
const doGet = (path, data) => {
    let url = `${location.protocol}//${location.host}${path}?`;

    for (let param in data) {
        url += `${param}=${data[param]}&`;
    }
    url = url.replace(/&$/, '');
    console.log(`url=${url}`);
    window.location.href=url;
};

sc_flag = false;

scroll_handler = (event) => {
    console.log(`event=${event}, sc_flag=${sc_flag}`);

    if ( ! sc_flag ) {
        return;
    }

    const el_search = document.getElementById("search_str");
    //console.log(`onscroll:search_str="${el_search.value}"`);
    if (el_search.value != "") {
        return;
    }

    const y = window.pageYOffset;
    const tail = window.pageYOffset + window.innerHeight;
    const bodyH = document.body.clientHeight;
    console.log(`${y}-${bodyH - tail}`);
    
    if (y < 70) {
        sc_flag = false;
        el = document.getElementById("date_from");
        date = el.value;
        console.log(`date=${date}`);
        doPost('/ytsched/', {date: date, top_bottom: "top"});
    }
    if (bodyH - tail < 90) {
        sc_flag = false;
        el = document.getElementById("date_to");
        date = el.value;
        console.log(`date=${date}`);
        doPost('/ytsched/', {date: date, top_bottom: "bottom"});
    }
};

/**
 *
 */
const scrollToId = (id, behavior = "auto") => {
    sc_flag = false;
    
    console.log(`id=${id}`);
    const el = document.getElementById(id);
    if (el == null) {
        console.log(`scrollToID:el=${el}`);
        return false;
    }

    if (document.documentElement.clientHeight >
        document.body.clientHeight) {
        return true;
    }

    const tail = el.offsetTop + window.innerHeight;
    if (tail > document.body.clientHeight) {
        console.log(`scrollToId:${tail} > ${document.body.clientHeight}`);

        return true;
        return false;
    }

    const el2 = document.getElementById("top_bottom");
    if (el2.value == "bottom") {
        el.scrollIntoView({block: "end", inline: "nearest",
                           behavior: "auto"});
        scrollBy({left: 0, top: +3, behavior: behavior});
    } else {
        el.scrollIntoView({block:"start", inline: "nearest",
                           behavior: "auto"});
        scrollBy({left: 0, top: -70, behavior: behavior});

    }

    sc_flag = true;

    return true;
};

/**
 *
 */
const scrollToDate = (path, date, behavior = "auto") => {
    sc_flag = false;
    
    console.log(`date=${date}`);
    if (scrollToId(`date-${date}`, behavior)) {
        const el = document.getElementById("cur_day");
        el.value = date;

        sc_flag = true;
    
        return true;
    }

    doPost(path, {date: date});
    return false;
};

/**
 *
 */
const moveDays = (path, days, behavior = "auto") => {
    const el = document.getElementById("cur_day");
    let d1 = new Date(el.value);
    d1.setDate(d1.getDate() + days);
    console.log(`d1=${d1}`);

    d1_str = d1.toISOString().replace(/T.*$/, '');
    scrollToDate(path, d1_str, behavior);
};
