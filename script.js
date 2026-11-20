const capabilities = {
  payments: {number:'01 / PAYMENTS',title:'Payment acceptance & acquiring',description:'Accept payments across markets with an infrastructure stack designed around the customer, jurisdiction and transaction flow.',items:['Global and domestic card acquiring','Gateways, hosted checkout and API acceptance','Open banking and local payment methods','Multi-acquirer routing and approval-rate optimisation'],outcome:'Collect locally. Route intelligently. Settle globally.'},
  banking: {number:'02 / BANKING',title:'Global banking & accounts',description:'Coordinate the account structures required to receive, hold and settle funds across jurisdictions and currencies.',items:['Corporate and multi-currency account access through partners','Named, virtual and segregated IBAN structures where available','SEPA, SWIFT, ACH, Faster Payments and local rails','Reconciliation and reporting options'],outcome:'Make banking part of the payment architecture.'},
  payouts: {number:'03 / PAYOUTS',title:'Global payouts & disbursements',description:'Move money to sellers, employees, affiliates, creators, suppliers and customers using suitable available rails.',items:['Bank and local account transfers','Card and wallet payout methods where available','Mass payout files and API-driven disbursement','Refunds, settlements and customer withdrawals'],outcome:'Pay one or pay thousands across the rails that fit.'},
  treasury: {number:'04 / TREASURY',title:'Foreign exchange & treasury',description:'Coordinate conversion, settlement and liquidity between where revenue is collected and where capital needs to move.',items:['Spot FX and multi-currency conversion','Cross-border treasury and supplier settlement','Multi-provider rate comparison and liquidity sourcing','Reporting, reconciliation and partner-led hedging options'],outcome:'Reduce friction across currencies and borders.'},
  assets: {number:'05 / DIGITAL ASSETS',title:'Stablecoin & digital asset settlement',description:'Use digital assets as an additional settlement and liquidity rail when they make commercial and regulatory sense.',items:['Fiat-to-digital-asset and off-ramp pathways','Supported stablecoin settlement corridors','Institutional OTC and wholesale liquidity access','Digital-asset processing through regulated counterparties'],outcome:'Use the rail that makes sense for the flow.'},
  cards: {number:'06 / EMBEDDED FINANCE',title:'Cards, wallets & embedded finance',description:'Extend the payment experience into programmable accounts, cards and wallets through issuer and programme partners.',items:['Virtual and physical card programmes','Prepaid, debit, expense and corporate cards','Multi-currency and wallet-linked structures','Controls, permissions, limits and reporting'],outcome:'Make payments part of the customer product.'},
  risk: {number:'07 / INTELLIGENCE',title:'Risk, compliance & payment intelligence',description:'Understand the merchant, transaction flow and provider risk appetite before money moves.',items:['KYB and ownership-readiness workflows','Jurisdiction, MCC and business-model assessment','Chargeback and refund performance monitoring','Provider risk mapping and reporting controls'],outcome:'Route good business with the right information.'}
};

const tabs = [...document.querySelectorAll('.cap-tab')];
const panel = document.querySelector('#cap-panel');
function selectCapability(tab, focus = false) {
  const data = capabilities[tab.dataset.cap];
  tabs.forEach(item => { const active = item === tab; item.classList.toggle('active',active); item.setAttribute('aria-selected',String(active)); item.tabIndex = active ? 0 : -1; });
  panel.setAttribute('aria-labelledby',tab.id);
  document.querySelector('#cap-number').textContent = data.number;
  document.querySelector('#cap-title').textContent = data.title;
  document.querySelector('#cap-description').textContent = data.description;
  document.querySelector('#cap-outcome').textContent = data.outcome;
  document.querySelector('#cap-list').replaceChildren(...data.items.map(item => { const li = document.createElement('li'); li.textContent = item; return li; }));
  if (focus) tab.focus();
}
tabs.forEach((tab,index) => {
  tab.addEventListener('click',() => selectCapability(tab));
  tab.addEventListener('keydown',event => {
    let next;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next !== undefined) { event.preventDefault(); selectCapability(tabs[next],true); }
  });
});

const menuButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('.primary-nav');
function closeMenu() { nav.classList.remove('open'); menuButton.setAttribute('aria-expanded','false'); menuButton.setAttribute('aria-label','Open menu'); }
menuButton.addEventListener('click',() => { const open = nav.classList.toggle('open'); menuButton.setAttribute('aria-expanded',String(open)); menuButton.setAttribute('aria-label',open ? 'Close menu' : 'Open menu'); });
nav.querySelectorAll('a').forEach(link => link.addEventListener('click',closeMenu));
document.addEventListener('keydown',event => { if (event.key === 'Escape') closeMenu(); });
document.querySelector('#year').textContent = new Date().getFullYear();
