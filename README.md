const nso_promotion_map = {
  "NSO Austria": "AT AAZ",
  "NSO Belgium": "BE AAS",
  "NSO Switzerland": "CH ANN",
  "NSO Germany": "DE AAU",
  "NSO Denmark": "DK ATV",
  "NSO Spain": "ES AAV",
  "NSO Finland": "FI ABL",
  "NSO France": "FR AAY",
  "NSO UK": "GB AAP",
  "NSO Ireland": "IE AEM",
  "NSO Italy": "IT ABA",
  "NSO Netherlands": "NL AAT",
  "NSO Netherlands 2": "NL ABX",
  "NSO Norway": "NO ARK",
  "NSO Portugal": "PT AYI",
  "NSO Sweden": "SE ABG"
};

function getPromotionText(nsoCountry) {
  const code = nso_promotion_map[nsoCountry];
  if (!code) return null;

  return `${code} ITCG ELP On Invoice Promotion (GLB)`;
}

