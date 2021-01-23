/**
 *   (c) 2021 Yoichi Tanibayashi
 */

/**
 *
 */
const doPost = (path, data) => {
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

/**
 *
 */
const scrollToId = (id, bottom, behavior = "auto") => {
    //console.log(`id=${id}`);
    const el = document.getElementById(id);
    if (el == null) {
        return false;
    }

    const tail = el.offsetTop + window.innerHeight;
    if (tail > document.body.clientHeight) {
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
    
    //el.scrollIntoView(true);
    return true;
};

/**
 *
 */
const scrollToDate = (path, date, behavior = "auto") => {
    if (scrollToId(`date-${date}`, "top", behavior)) {
        const el = document.getElementById("cur_day");
        el.value = date;
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
