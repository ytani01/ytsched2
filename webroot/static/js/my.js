/**
 *   (c) 2021 Yoichi Tanibayashi
 */
const ID_MSG_AREA = "message_area";
const ID_MY_NAME = "my_name";
const ID_MY_MSG = "my_msg";

const cookieObj = new MyCookie();
let myName = "";

let curDay = new Date();

/**
 * 'http://host:port/aaa/bbb/' -> 'ws://host:port/aaa/ws'
 * 'https://host:port/aaa/bbb/' -> 'wss://host:port/aaa/ws'
 */
const WS_PROTO = location.protocol.replace('http', 'ws');
const WS_URL = `${WS_PROTO}//${location.host}/`
      + `${location.pathname.split('/')[1]}/ws/`;
console.log(`WS_URL=${WS_URL}`);

/**
 * websocket は、常に open の状態にして、メッセージ待ち受ける
 *
 *  - ``window.onload``, ``ws.onclose`` で、``connect_ws()``
 *  - 送信時は、いきなり ``ws.send()``
 */
let wsObj = undefined;

/**
 *
 */
const connect_ws = () => {
    wsObj = new WebSocket(WS_URL);

    wsObj.onclose = () => {
        console.log(`onclose()`);
        const el = document.getElementById(ID_MSG_AREA);
        el.value = '';
        connect_ws();  // reconnect
    };

    wsObj.onmessage = (event) => {
        const msg = event.data;
        console.log(`onmessage(): msg=${msg}`);

        const el = document.getElementById(ID_MSG_AREA);
        el.value += msg;
        el.scrollTop = el.scrollHeight; // 最下部にスクロールする
    };
};

/**
 * @param {string} msg_id
 */
const send_msg = () => {
    const el_msg = document.getElementById(ID_MY_MSG);
    wsObj.send(`${myName}>${el_msg.value}`);
    el_msg.value = '';
};

/**
 * @param {string} name_id
 */
const set_name = () => {
    const el_name = document.getElementById(ID_MY_NAME);
    myName = el_name.value;
    console.log(`set_name("${ID_MY_NAME}"): ${myName}`);
    cookieObj.set(ID_MY_NAME, myName);
};

/***********************************************************/

/**
 *
 */
const execGet = (path, data) => {
    let url = `${location.protocol}//${location.host}${path}?`

    for (let param in data) {
        url += `${param}=${data[param]}&`
    }
    url = url.replace(/&$/, '');
    console.log(`url=${url}`);
    window.location.href=url;
};

const scrollToId = (id, bottom) => {
    console.log(`id=${id}`);

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
                           behavior:"auto"});
        scrollBy({left: 0, top: +3, behavior: "auto"});
    } else {
        el.scrollIntoView({block:"start", inline: "nearest",
                           behavior: "auto"});
        scrollBy({left: 0, top: -65, behavior: "auto"});

    }
    
    //el.scrollIntoView(true);
    return true;
};

const scrollToDate = (path, date) => {
    if (scrollToId(`date-${date}`)) {
        const el = document.getElementById("cur_day");
        el.value = date;
        return true;
    }
    execGet(path, {date: date});
    return false;
};

const moveDays = (path, days) => {
    const el = document.getElementById("cur_day");
    let d1 = new Date(el.value);
    d1.setDate(d1.getDate() + days);
    console.log(`d1=${d1}`);

    d1_str = d1.toISOString().replace(/T.*$/, '');
    scrollToDate(path, d1_str);
};

/**
window.onload = () => {
    console.log(`window.onload()`);
    connect_ws();

    myName = cookieObj.get(ID_MY_NAME);
    if (myName === undefined) {
        myName = "";
    }
    console.log(`window.onload(): myName=${myName}`);

    const el_name = document.getElementById(ID_MY_NAME);
    el_name.value = myName;
};
*/
