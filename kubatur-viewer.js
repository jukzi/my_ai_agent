(() => {
  const polarPoint=(r,a)=>[.5+r*Math.cos(a),.5+r*Math.sin(a)];
  const radicalInverse=(n,base)=>{let value=0, place=1/base;while(n){value+=(n%base)*place;n=Math.floor(n/base);place/=base;}return value;};
  // Fixed seed keeps the example reproducible across reloads.
  function randomExample(){
    let seed=407;
    function next(){seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed/4294967296;}
    return Array.from({length:64},()=>[next(),next()]);
  }
  const terrainVertices=Array.from({length:121},(_,i)=>{
    const x=(i%11)/10,y=Math.floor(i/11)/10;
    return [x,(x*x+y*y)/2,y];
  });
  const triangleOutline={v:[[0,0],[1,0],[0,1]],faces:[[0,1,2]]};
  const cases = {
    triangleEdges: {...triangleOutline,points:[[.5,0],[.5,.5],[0,.5]]},
    terrain: {v:terrainVertices,faces:Array.from({length:100},(_,i)=>{
      const j=Math.floor(i/10)*11+i%10;return [j,j+1,j+12,j+11];
    }),points:[.25,.75].flatMap(x=>[.25,.75].map(y=>[x,(x*x+y*y)/2,y]))},
    oneCell: {v:[[0,0],[1,0],[1,1],[0,1]],faces:[[0,1,2,3]],points:[[.5,.5]]},
    fourCells: {v:[[0,0],[1,0],[1,1],[0,1]],faces:[[0,1,2,3]], divisions:2,
      points:[.25,.75].flatMap(x=>[.25,.75].map(y=>[x,y]))},
    randomSquare: {v:[[0,0],[1,0],[1,1],[0,1]],faces:[[0,1,2,3]],pointSize:3.5, grid:true,points:randomExample()},
    halton: {v:[[0,0],[1,0],[1,1],[0,1]],faces:[[0,1,2,3]],pointSize:3.5, grid:true,
      points:Array.from({length:64},(_,i)=>[radicalInverse(i+1,2),radicalInverse(i+1,3)])},
    noise: {v:[[0,0],[1,0],[0,1]],faces:[],noise:true,
      curve:Array.from({length:64},(_,i)=>[i/63,1/Math.sqrt(i+1)]),
      points:[1,4,16,64].map(n=>[(n-1)/63,1/Math.sqrt(n)])},
    midpoint: {v:[[0,0],[1,0],[1,.25],[0,.25]], faces:[[0,1,2,3]], points:[[.5,.25]],
      curve:Array.from({length:81},(_,i)=>[i/80,(i/80)**2])},
    gauss: {v:[[0,.5],[1,.5]], faces:[], interval:true, points:[-1,1].map(i=>[.5+i/(2*Math.sqrt(3)),.5])},
    disk: {v:[[0,0]], faces:[], rings:[.44], guides:[.44*2/3], points:[polarPoint(.44*2/3,Math.PI/5)], radiusLine:true},
    annulus: {v:[[0,0]], faces:[], rings:[.44,.44*.9], guides:[.915,.95,.985].map(r=>r*.44), pointSize:2.3,
      points:[.915,.95,.985].flatMap((r,j)=>Array.from({length:8},(_,i)=>polarPoint(.44*r,(i+j/3)*Math.PI/4)))},
    square: {v:[[0,0],[1,0],[1,1],[0,1]], faces:[[0,1,2,3]], points:[-1,1].flatMap(i=>[-1,1].map(j=>[.5+i/(2*Math.sqrt(3)),.5+j/(2*Math.sqrt(3))]))},
    cube: {v:[[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]], faces:[[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]], points:[-1,1].flatMap(i=>[-1,1].flatMap(j=>[-1,1].map(k=>[i,j,k].map(x=>.5+x/(2*Math.sqrt(3))))))},
    triangle: {v:[[0,0],[1,0],[0,1]], faces:[[0,1,2]], points:[[1/6,1/6],[2/3,1/6],[1/6,2/3]]},
    tetrahedron: {v:[[0,0,0],[1,0,0],[0,1,0],[0,0,1]], faces:[[0,1,2],[0,1,3],[0,2,3],[1,2,3]], points:Array.from({length:4},(_,i)=>Array.from({length:3},(_,j)=>1/4+(i===j?3:-1)/(4*Math.sqrt(5))))}
  };
  // Two roots of t² - t/12 - 1/80 = 0.
  const shiftRoot=Math.sqrt((1/12)**2+1/20);
  const triangleShiftRoot=Math.hypot(1/15,1/6);
  cases.trianglePositiveCubic={...triangleOutline,
    points:[1/15-triangleShiftRoot,1/15+triangleShiftRoot].flatMap(t=>{
      const a=1/3+2*t,b=1/3-t;
      return [[a,b],[b,a],[b,b]];
    })};
  const edgeGauss=[.5-Math.sqrt(1/12),.5+Math.sqrt(1/12)];
  cases.triangleBoundaryQuartic={...triangleOutline,negativePoints:[0,1,2],
    points:[...triangleOutline.v,[1/3,1/3],...edgeGauss.flatMap(t=>[[t,0],[0,t],[t,1-t]])]};
  cases.triangleBoundaryCubic={...triangleOutline,
    points:[...triangleOutline.v,...cases.triangleEdges.points,[1/3,1/3]]};
  const quarticA=(Math.sqrt(10)-2)/9, quarticB=2/45-2*quarticA/15;
  const quarticDelta=Math.sqrt(quarticA**2+4*quarticB);
  cases.triangleQuartic={...triangleOutline,
    points:[(quarticA-quarticDelta)/2,(quarticA+quarticDelta)/2].flatMap(t=>{
      const a=1/3+2*t,b=1/3-t;
      return [[a,b],[b,a],[b,b]];
    })};
  cases.triangleSigned={...triangleOutline,negativePoint:0,
    points:[[1/3,1/3],[3/5,1/5],[1/5,3/5],[1/5,1/5]]};
  cases.tetrahedronPositiveCubic={...cases.tetrahedron,
    points:[(1/12-shiftRoot)/2,(1/12+shiftRoot)/2].flatMap(t=>
      Array.from({length:4},(_,i)=>Array.from({length:3},(_,j)=>1/4+(i===j?3:-1)*t)))};
  cases.tetrahedronSigned={...cases.tetrahedron,negativePoint:0,points:[[.25,.25,.25],
    ...Array.from({length:4},(_,i)=>Array.from({length:3},(_,j)=>i===j?1/2:1/6))]};
  cases.tetrahedronQuadraticGrid={...cases.tetrahedron,
    points:[...cases.tetrahedron.v,...cases.tetrahedron.v.flatMap((a,i)=>
      cases.tetrahedron.v.slice(i+1).map(b=>a.map((x,k)=>(x+b[k])/2)))]};
  const keastOffset=Math.sqrt(5/224);
  cases.tetrahedronQuartic={...cases.tetrahedron,negativePoint:0,
    points:[[.25,.25,.25],
      ...Array.from({length:4},(_,i)=>Array.from({length:3},(_,j)=>i===j?11/14:1/14)),
      ...[0,1,2,3].flatMap(i=>[0,1,2,3].filter(j=>j>i).map(j=>
        [0,1,2].map(k=>.25+(k===i||k===j?keastOffset:-keastOffset))))]};
  const permutations4=([a,b,c,d])=>[a,b,c,d].flatMap((v,i,all)=>
    all.filter((_,j)=>j!==i).flatMap((w,j,tail)=>{
      const [x,y]=tail.filter((_,k)=>k!==j);return [[v,w,x,y],[v,w,y,x]];
    }));
  const orbit4=seed=>[...new Map(permutations4(seed).map(point=>[point.join(','),point])).values()];
  cases.tetrahedronFaceOrbits={...cases.tetrahedron,
    points:[[.25,.25,.25],...[ [1,0,0,0],[1/3,1/3,1/3,0],[.5,.25,.25,0] ].flatMap(orbit4).map(point=>point.slice(0,3))],
    negativePoints:[5,6,7,8],pointSize:4};
  const boundarySeeds=[[5,0,0,0],[4,1,0,0],[3,2,0,0],[3,1,1,0],[2,2,1,0]];
  const boundaryGroups=boundarySeeds.map(seed=>orbit4(seed).map(point=>point.slice(0,3).map(k=>k/5)));
  cases.tetrahedronBoundaryGrid={...cases.tetrahedron,pointSize:3,
    points:[[.25,.25,.25],...boundaryGroups.flat()],
    negativePoints:[1,4].flatMap(group=>boundaryGroups[group].map((_,i)=>
      1+i+boundaryGroups.slice(0,group).reduce((n,points)=>n+points.length,0)))};
  // Published Worku–Hicken–Zingg table, mapped to the unit tetrahedron.
  cases.tetrahedronPositiveQuartic={...cases.tetrahedron,pointSize:5,points:[[0.08401862525144627,0.08401862525144627,0.7479441242456613],[0.08401862525144627,0.7479441242456613,0.08401862525144627],[0.08401862525144627,0.08401862525144627,0.08401862525144627],[0.7479441242456613,0.08401862525144627,0.08401862525144627],[0.3094941673685986,0.3094941673685986,0.07151749789420436],[0.3094941673685986,0.07151749789420436,0.3094941673685986],[0.3094941673685986,0.3094941673685986,0.3094941673685986],[0.07151749789420436,0.3094941673685986,0.3094941673685986],[0.42433689920607076,0.07566310079392924,0.07566310079392924],[0.07566310079392924,0.42433689920607076,0.07566310079392924],[0.07566310079392924,0.07566310079392924,0.42433689920607076],[0.42433689920607076,0.42433689920607076,0.07566310079392924],[0.42433689920607076,0.07566310079392924,0.42433689920607076],[0.07566310079392924,0.42433689920607076,0.42433689920607076]]};
  cases.tetrahedronCentroid={...cases.tetrahedron,points:[[.25,.25,.25]]};
  cases.cubeFaces={...cases.cube,points:[0,1,2].flatMap(axis=>[0,1].map(side=>[.5,.5,.5].map((v,i)=>i===axis?side:v)))};
  // Worku–Hicken–Zingg, published degree-40 table on the unit triangle.
  cases.triangleDegree40={...triangleOutline,pointSize:2,points:[[0.0027508009372958,0.9944983981254084],[0.0027508009372958,0.0027508009372958],[0.9944983981254085,0.0027508009372958],[0.0172025450572428,0.9655949098855143],[0.0172025450572427,0.0172025450572428],[0.9655949098855143,0.0172025450572428],[0.0387396121403619,0.9225207757192762],[0.0387396121403619,0.0387396121403619],[0.9225207757192762,0.0387396121403619],[0.0637844203517565,0.872431159296487],[0.0637844203517565,0.0637844203517565],[0.8724311592964871,0.0637844203517565],[0.0986165154182953,0.8027669691634094],[0.0986165154182953,0.0986165154182953],[0.8027669691634094,0.0986165154182953],[0.1317525030919222,0.7364949938161557],[0.1317525030919221,0.1317525030919222],[0.7364949938161557,0.1317525030919222],[0.1689580886170887,0.6620838227658227],[0.1689580886170887,0.1689580886170887],[0.6620838227658227,0.1689580886170887],[0.232248428840358,0.535503142319284],[0.232248428840358,0.232248428840358],[0.535503142319284,0.232248428840358],[0.255205841459073,0.489588317081854],[0.255205841459073,0.255205841459073],[0.489588317081854,0.255205841459073],[0.2937751178239469,0.4124497643521062],[0.2937751178239469,0.2937751178239469],[0.4124497643521062,0.2937751178239469],[0.4986095713846501,0.0027808572306999],[0.4986095713846501,0.4986095713846501],[0.0027808572306999,0.4986095713846501],[0.4924240605422714,0.0151518789154572],[0.4924240605422714,0.4924240605422714],[0.0151518789154572,0.4924240605422714],[0.4794545568218644,0.0410908863562711],[0.4794545568218644,0.4794545568218644],[0.0410908863562711,0.4794545568218644],[0.4608551903522611,0.0782896192954778],[0.4608551903522611,0.4608551903522611],[0.0782896192954778,0.4608551903522611],[0.4363196941891612,0.1273606116216776],[0.4363196941891612,0.4363196941891612],[0.1273606116216776,0.4363196941891612],[0.4065211341125968,0.1869577317748063],[0.4065211341125968,0.4065211341125968],[0.1869577317748063,0.4065211341125968],[0.3713817324330683,0.2572365351338635],[0.3713817324330683,0.3713817324330683],[0.2572365351338635,0.3713817324330683],[0.0032477217571192,0.0148483834381692],[0.9819038948047116,0.0148483834381692],[0.9819038948047116,0.0032477217571192],[0.0032477217571192,0.9819038948047116],[0.0148483834381692,0.9819038948047116],[0.0148483834381692,0.0032477217571192],[0.0031340703228931,0.0368419614548818],[0.960023968222225,0.0368419614548818],[0.960023968222225,0.0031340703228931],[0.0031340703228931,0.960023968222225],[0.0368419614548818,0.960023968222225],[0.0368419614548818,0.0031340703228931],[0.0021836781948182,0.0686166278225283],[0.9291996939826535,0.0686166278225283],[0.9291996939826535,0.0021836781948182],[0.0021836781948182,0.9291996939826535],[0.0686166278225283,0.9291996939826535],[0.0686166278225283,0.0021836781948182],[0.0022639407189322,0.1119970887043906],[0.8857389705766772,0.1119970887043906],[0.8857389705766772,0.0022639407189322],[0.0022639407189323,0.8857389705766772],[0.1119970887043906,0.8857389705766772],[0.1119970887043906,0.0022639407189322],[0.0035737405952508,0.1641678124694017],[0.8322584469353475,0.1641678124694017],[0.8322584469353476,0.0035737405952509],[0.0035737405952509,0.8322584469353475],[0.1641678124694017,0.8322584469353475],[0.1641678124694017,0.0035737405952509],[0.000510478348399,0.2235775319639128],[0.7759119896876882,0.2235775319639128],[0.7759119896876882,0.000510478348399],[0.000510478348399,0.7759119896876882],[0.2235775319639128,0.7759119896876882],[0.2235775319639128,0.000510478348399],[0.0035679623123716,0.2881899169050946],[0.7082421207825338,0.2881899169050946],[0.7082421207825338,0.0035679623123716],[0.0035679623123716,0.7082421207825338],[0.2881899169050946,0.7082421207825338],[0.2881899169050946,0.0035679623123716],[0.0020238229879074,0.3593797542236113],[0.6385964227884813,0.3593797542236113],[0.6385964227884813,0.0020238229879074],[0.0020238229879074,0.6385964227884813],[0.3593797542236113,0.6385964227884813],[0.3593797542236113,0.0020238229879074],[0.0027303201690263,0.4305025156827059],[0.5667671641482679,0.4305025156827059],[0.5667671641482679,0.0027303201690263],[0.0027303201690262,0.5667671641482679],[0.4305025156827059,0.5667671641482679],[0.4305025156827059,0.0027303201690263],[0.0157313861305279,0.0419222481523173],[0.9423463657171548,0.0419222481523173],[0.9423463657171548,0.0157313861305279],[0.015731386130528,0.9423463657171548],[0.0419222481523172,0.9423463657171548],[0.0419222481523173,0.0157313861305279],[0.0118949131506759,0.0754025518231636],[0.9127025350261605,0.0754025518231636],[0.9127025350261605,0.0118949131506759],[0.0118949131506759,0.9127025350261605],[0.0754025518231636,0.9127025350261605],[0.0754025518231636,0.0118949131506759],[0.0132198786357128,0.1173799568243216],[0.8694001645399656,0.1173799568243216],[0.8694001645399656,0.0132198786357128],[0.0132198786357128,0.8694001645399656],[0.1173799568243216,0.8694001645399656],[0.1173799568243216,0.0132198786357128],[0.0190702400850086,0.1667299724976037],[0.8141997874173877,0.1667299724976037],[0.8141997874173877,0.0190702400850086],[0.0190702400850086,0.8141997874173877],[0.1667299724976037,0.8141997874173877],[0.1667299724976037,0.0190702400850086],[0.0097154933051948,0.2220210233800836],[0.7682634833147216,0.2220210233800836],[0.7682634833147216,0.0097154933051948],[0.0097154933051948,0.7682634833147216],[0.2220210233800836,0.7682634833147216],[0.2220210233800836,0.0097154933051948],[0.0186413731362191,0.2782719028554982],[0.7030867240082828,0.2782719028554982],[0.7030867240082828,0.0186413731362191],[0.0186413731362191,0.7030867240082828],[0.2782719028554982,0.7030867240082828],[0.2782719028554982,0.0186413731362191],[0.0132019015352808,0.3469798490306024],[0.6398182494341168,0.3469798490306024],[0.6398182494341168,0.0132019015352807],[0.0132019015352807,0.6398182494341168],[0.3469798490306025,0.6398182494341168],[0.3469798490306025,0.0132019015352807],[0.0123267175748394,0.4161952497120543],[0.5714780327131063,0.4161952497120543],[0.5714780327131063,0.0123267175748394],[0.0123267175748394,0.5714780327131063],[0.4161952497120543,0.5714780327131063],[0.4161952497120543,0.0123267175748394],[0.0321885180936544,0.0732382683858624],[0.8945732135204831,0.0732382683858624],[0.8945732135204831,0.0321885180936545],[0.0321885180936545,0.8945732135204831],[0.0732382683858624,0.8945732135204831],[0.0732382683858624,0.0321885180936545],[0.0326366389762738,0.1149827564195359],[0.8523806046041903,0.1149827564195359],[0.8523806046041903,0.0326366389762738],[0.0326366389762738,0.8523806046041903],[0.1149827564195359,0.8523806046041903],[0.1149827564195359,0.0326366389762738],[0.0461888997506913,0.1585106661311003],[0.7953004341182084,0.1585106661311003],[0.7953004341182084,0.0461888997506913],[0.0461888997506913,0.7953004341182084],[0.1585106661311003,0.7953004341182084],[0.1585106661311003,0.0461888997506913],[0.032851411890502,0.2182212445204006],[0.7489273435890975,0.2182212445204006],[0.7489273435890975,0.0328514118905021],[0.0328514118905021,0.7489273435890974],[0.2182212445204005,0.7489273435890974],[0.2182212445204005,0.0328514118905021],[0.0346673557802011,0.2919602978795548],[0.6733723463402441,0.2919602978795548],[0.6733723463402441,0.0346673557802011],[0.0346673557802011,0.6733723463402441],[0.2919602978795548,0.6733723463402441],[0.2919602978795548,0.0346673557802011],[0.0357778762225466,0.3491460288519457],[0.6150760949255079,0.3491460288519457],[0.6150760949255077,0.0357778762225466],[0.0357778762225466,0.6150760949255077],[0.3491460288519456,0.6150760949255077],[0.3491460288519456,0.0357778762225466],[0.0289652362455958,0.419655934226169],[0.5513788295282351,0.419655934226169],[0.5513788295282351,0.0289652362455958],[0.0289652362455958,0.5513788295282351],[0.419655934226169,0.5513788295282351],[0.419655934226169,0.0289652362455958],[0.0607693637367911,0.1044765609633648],[0.8347540752998441,0.1044765609633648],[0.8347540752998441,0.0607693637367911],[0.0607693637367911,0.8347540752998441],[0.1044765609633647,0.8347540752998441],[0.1044765609633648,0.0607693637367911],[0.0829231474541694,0.1474262899309621],[0.7696505626148685,0.1474262899309621],[0.7696505626148685,0.0829231474541694],[0.0829231474541695,0.7696505626148685],[0.147426289930962,0.7696505626148685],[0.1474262899309621,0.0829231474541694],[0.0673309289257916,0.2070652979801721],[0.7256037730940362,0.2070652979801721],[0.7256037730940362,0.0673309289257915],[0.0673309289257916,0.7256037730940362],[0.2070652979801722,0.7256037730940362],[0.2070652979801723,0.0673309289257915],[0.0532835862862027,0.2701934634076888],[0.6765229503061085,0.2701934634076888],[0.6765229503061085,0.0532835862862027],[0.0532835862862026,0.6765229503061085],[0.2701934634076888,0.6765229503061085],[0.2701934634076888,0.0532835862862027],[0.0704197160514134,0.3278715298750142],[0.6017087540735724,0.3278715298750142],[0.6017087540735724,0.0704197160514133],[0.0704197160514133,0.6017087540735724],[0.3278715298750143,0.6017087540735724],[0.3278715298750143,0.0704197160514133],[0.0590517065642104,0.4014634601818405],[0.5394848332539491,0.4014634601818405],[0.5394848332539491,0.0590517065642104],[0.0590517065642104,0.5394848332539491],[0.4014634601818405,0.5394848332539491],[0.4014634601818405,0.0590517065642104],[0.1123438394837496,0.1893220024641595],[0.6983341580520909,0.1893220024641595],[0.6983341580520909,0.1123438394837495],[0.1123438394837495,0.6983341580520909],[0.1893220024641596,0.6983341580520909],[0.1893220024641596,0.1123438394837495],[0.0936556477855718,0.2565508470126394],[0.6497935052017888,0.2565508470126394],[0.6497935052017888,0.0936556477855718],[0.0936556477855718,0.6497935052017888],[0.2565508470126394,0.6497935052017888],[0.2565508470126394,0.0936556477855718],[0.1100145623217876,0.3156427247433872],[0.5743427129348252,0.3156427247433872],[0.5743427129348252,0.1100145623217876],[0.1100145623217876,0.5743427129348252],[0.3156427247433872,0.5743427129348252],[0.3156427247433872,0.1100145623217876],[0.1012978714713529,0.38214524062799],[0.5165568879006571,0.38214524062799],[0.5165568879006571,0.1012978714713529],[0.1012978714713529,0.5165568879006571],[0.38214524062799,0.5165568879006571],[0.38214524062799,0.1012978714713529],[0.1437494799519344,0.2326692091403548],[0.6235813109077107,0.2326692091403548],[0.6235813109077107,0.1437494799519344],[0.1437494799519344,0.6235813109077107],[0.2326692091403548,0.6235813109077107],[0.2326692091403548,0.1437494799519344],[0.1390315511510855,0.2935843248952966],[0.5673841239536179,0.2935843248952966],[0.5673841239536179,0.1390315511510855],[0.1390315511510855,0.5673841239536179],[0.2935843248952966,0.5673841239536179],[0.2935843248952966,0.1390315511510855],[0.1922648556379415,0.2225059899251578],[0.5852291544369007,0.2225059899251578],[0.5852291544369007,0.1922648556379415],[0.1922648556379415,0.5852291544369007],[0.2225059899251578,0.5852291544369007],[0.2225059899251578,0.1922648556379415],[0.1876006405723769,0.2819576292757523],[0.5304417301518708,0.2819576292757523],[0.5304417301518708,0.1876006405723769],[0.1876006405723769,0.5304417301518708],[0.2819576292757523,0.5304417301518708],[0.2819576292757523,0.1876006405723769],[0.1551998886019634,0.356126781587416],[0.4886733298106206,0.356126781587416],[0.4886733298106206,0.1551998886019634],[0.1551998886019634,0.4886733298106206],[0.356126781587416,0.4886733298106206],[0.356126781587416,0.1551998886019634],[0.2204067411876406,0.3281435693931578],[0.4514496894192017,0.3281435693931578],[0.4514496894192017,0.2204067411876406],[0.2204067411876406,0.4514496894192017],[0.3281435693931578,0.4514496894192017],[0.3281435693931578,0.2204067411876406],[0.3333333333333334,0.3333333333333334]]};
  for (const host of document.querySelectorAll('[data-kubatur-viewer]')) {
    const scene=cases[host.dataset.kubaturViewer]; if(!scene) continue;
    const spatial=scene.v[0].length===3;
    const center=spatial ? [0,1,2].map(axis=>{
      const values=scene.v.map(vertex=>vertex[axis]);
      return (Math.min(...values)+Math.max(...values))/2;
    }) : [.5,.5,0];
    const canvas=document.createElement('canvas'); canvas.width=640; canvas.height=420; canvas.tabIndex=0;
    canvas.setAttribute('aria-label','Interaktive Abbildung: Pfeiltasten zum Verschieben, Plus und Minus zum Zoomen');
    const ctx=canvas.getContext('2d'); if(!ctx) continue;
    const controls=document.createElement('div'); controls.className='viewer-controls';
    host.append(canvas,controls);
    const icons={plus:'M12 5v14M5 12h14',minus:'M5 12h14',reset:'M4 10a8 8 0 1 1 1 7M4 4v6h6',left:'M20 11a8 8 0 0 0-14-4L3 10m0-6v6h6',right:'M4 11a8 8 0 0 1 14-4l3 3m0-6v6h-6',full:'M9 4H4v5m11-5h5v5M4 15v5h5m11-5v5h-5',exit:'M4 9h5V4m11 5h-5V4M4 15h5v5m11-5h-5v5'};
    function appearance(btn,label,icon){btn.title=label;btn.setAttribute('aria-label',label);btn.innerHTML=`<svg aria-hidden="true" viewBox="0 0 24 24"><path d="${icons[icon]}"/></svg>`;}
    let zoom,dx,dy,a,b;
    function reset(){zoom=1;dx=dy=0;a=spatial?0.65:0;b=spatial?0.5:0;draw();}
    function project([x,y,z=0]){
      x-=center[0];y-=center[1];z-=center[2];
      const X=x*Math.cos(a)-z*Math.sin(a), Z=x*Math.sin(a)+z*Math.cos(a);
      const Y=y*Math.cos(b)-Z*Math.sin(b);
      return [320+dx+220*zoom*X,210+dy-220*zoom*Y,y*Math.sin(b)+Z*Math.cos(b)];
    }
    function draw(){
      ctx.clearRect(0,0,640,420);
      if(scene.rings){
        const [cx,cy]=project([.5,.5]);
        const circle=r=>{ctx.moveTo(cx+r*220*zoom,cy);ctx.arc(cx,cy,r*220*zoom,0,2*Math.PI);};
        ctx.beginPath();scene.rings.forEach(circle);ctx.fillStyle='#5eead445';ctx.fill('evenodd');ctx.strokeStyle='#327c81';ctx.lineWidth=2;ctx.stroke();
        ctx.save();ctx.setLineDash([4,4]);ctx.strokeStyle='#46888d';ctx.lineWidth=1;ctx.beginPath();scene.guides.forEach(circle);ctx.stroke();ctx.restore();
        if(scene.radiusLine){const [x,y]=project(scene.points[0]);ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(x,y);ctx.stroke();}
      }
      const v=scene.v.map(project);
      if(scene.interval){
        const [left,right]=v;
        ctx.strokeStyle='#327c81';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(left[0],left[1]);ctx.lineTo(right[0],right[1]);
        for(const [x,y] of v){ctx.moveTo(x,y-8);ctx.lineTo(x,y+8);}ctx.stroke();
        ctx.font='15px system-ui';ctx.textAlign='center';ctx.fillStyle='#153743';
        v.forEach(([x,y],i)=>ctx.fillText(String(i),x,y+29));
        scene.points.forEach((p,i)=>{const [x,y]=project(p);ctx.fillText(i?'½ + 1/(2√3)':'½ − 1/(2√3)',x,y-17);});
      }
      const depth=f=>f.reduce((s,i)=>s+v[i][2],0)/f.length;
      for(const f of [...scene.faces].sort((l,r)=>depth(l)-depth(r))){
        ctx.beginPath(); f.forEach((i,j)=>j?ctx.lineTo(...v[i].slice(0,2)):ctx.moveTo(...v[i].slice(0,2)));ctx.closePath();ctx.fillStyle='#5eead445';ctx.fill();ctx.strokeStyle='#327c81';ctx.lineWidth=2;ctx.stroke();
      }
      if(scene.noise){
        const [origin,right,top]=v;
        ctx.beginPath();ctx.moveTo(...right.slice(0,2));ctx.lineTo(...origin.slice(0,2));ctx.lineTo(...top.slice(0,2));ctx.strokeStyle='#327c81';ctx.lineWidth=2;ctx.stroke();
        ctx.font='15px system-ui';ctx.fillStyle='#153743';ctx.textAlign='center';
        for(const n of [1,16,64]){const [x,y]=project([(n-1)/63,0]);ctx.fillText(String(n),x,y+20);}
        ctx.fillText('Messungen',right[0]+48,right[1]+20);ctx.fillText('Relative Streuung',top[0]+58,top[1]-15);
      }
      if(scene.grid || scene.divisions){
        const divisions=scene.divisions ?? 4;
        ctx.save();ctx.setLineDash([3,4]);ctx.strokeStyle='#327c81';ctx.lineWidth=1;ctx.beginPath();
        for(let i=1;i<divisions;i++){
          const a=i/divisions;
          for(const [start,end] of [[[a,0],[a,1]],[[0,a],[1,a]]]){
            ctx.moveTo(...project(start).slice(0,2));ctx.lineTo(...project(end).slice(0,2));
          }
        }
        ctx.stroke();ctx.restore();
      }
      if(scene.curve){
        const trace=points=>points.forEach((p,i)=>{const [x,y]=project(p);if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);});
        ctx.beginPath();trace(scene.curve);const [x,y]=project([1,0]);ctx.lineTo(x,y);ctx.closePath();ctx.fillStyle='#2563eb24';if(!scene.noise)ctx.fill();
        ctx.beginPath();trace(scene.curve);ctx.strokeStyle='#244ab5';ctx.lineWidth=3;ctx.stroke();
      }
      // Draw signed markers last so the negative symbol remains visible.
      const markers=scene.points.map((point,i)=>({point,negative:i===scene.negativePoint || (scene.negativePoints?.includes(i) ?? false)}));
      markers.sort((a,b)=>Number(a.negative)-Number(b.negative));
      for(const {point,negative} of markers){
        const [x,y]=project(point), r=scene.pointSize??7;
        ctx.beginPath();
        if(negative){ctx.moveTo(x,y-r-2);ctx.lineTo(x+r+2,y);ctx.lineTo(x,y+r+2);ctx.lineTo(x-r-2,y);ctx.closePath();}
        else ctx.arc(x,y,r,0,2*Math.PI);
        ctx.fillStyle=negative?'#6941a5':'#d65b28';ctx.fill();ctx.strokeStyle='white';ctx.lineWidth=1.5;ctx.stroke();
        if(negative){ctx.beginPath();ctx.moveTo(x-3,y);ctx.lineTo(x+3,y);ctx.stroke();}
      }
    }
    function magnify(f){zoom=Math.max(.3,Math.min(8,zoom*f));draw();}
    function button(label,icon,fn){const btn=document.createElement('button');btn.type='button';appearance(btn,label,icon);btn.addEventListener('click',fn);controls.append(btn);return btn;}
    button('Vergrößern','plus',()=>magnify(1.2));button('Verkleinern','minus',()=>magnify(1/1.2));button('Zurücksetzen','reset',reset);
    if(spatial){button('Links drehen','left',()=>{a-=.2;draw();});button('Rechts drehen','right',()=>{a+=.2;draw();});}
    if(host.requestFullscreen){const btn=button('Vollbild','full',async()=>{try{if(document.fullscreenElement===host)await document.exitFullscreen();else await host.requestFullscreen();}catch{appearance(btn,'Vollbild nicht verfügbar','full');}});document.addEventListener('fullscreenchange',()=>{const active=document.fullscreenElement===host;appearance(btn,active?'Vollbild verlassen':'Vollbild',active?'exit':'full');});}
    canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();magnify(Math.exp(-Math.sign(e.deltaY)*.12));},{passive:false});
    canvas.addEventListener('keydown',e=>{const moves={ArrowLeft:[-15,0],ArrowRight:[15,0],ArrowUp:[0,-15],ArrowDown:[0,15]};if(moves[e.key]){const [x,y]=moves[e.key];dx+=x;dy+=y;draw();}else if(e.key==='+'||e.key==='=')magnify(1.2);else if(e.key==='-')magnify(1/1.2);else return;e.preventDefault();});
    if(scene.grid){
      const counts=Array(16).fill(0);
      for(const [x,y] of scene.points) counts[4*Math.floor(4*y)+Math.floor(4*x)]++;
      const panel=document.createElement('details');panel.className='viewer-counts';
      const summary=document.createElement('summary');summary.textContent='Punkte je Rasterfeld';panel.append(summary);
      const table=document.createElement('table');
      const caption=table.createCaption();caption.textContent='Anzahl pro Feld, von oben links gelesen';
      for(let row=3;row>=0;row--){const tr=table.insertRow();for(let col=0;col<4;col++)tr.insertCell().textContent=counts[4*row+col];}
      panel.append(table);host.after(panel);
    }
    const pointers=new Map();
    canvas.addEventListener('pointerdown',e=>{if(e.button!==0)return;canvas.setPointerCapture(e.pointerId);canvas.focus({preventScroll:true});pointers.set(e.pointerId,[e.clientX,e.clientY]);});
    canvas.addEventListener('pointermove',e=>{
      if(!pointers.has(e.pointerId))return;
      const old=[...pointers.values()];pointers.set(e.pointerId,[e.clientX,e.clientY]);const next=[...pointers.values()];
      const scale=640/canvas.getBoundingClientRect().width;
      if(next.length===2){const dist=p=>Math.hypot(p[0][0]-p[1][0],p[0][1]-p[1][1]);const mid=(p,j)=>(p[0][j]+p[1][j])/2;dx+=(mid(next,0)-mid(old,0))*scale;dy+=(mid(next,1)-mid(old,1))*scale;if(dist(old)>0)magnify(dist(next)/dist(old));}
      else if(next.length===1){const x=(next[0][0]-old[0][0])*scale,y=(next[0][1]-old[0][1])*scale;if(spatial&&!e.shiftKey){a+=x/150;b+=y/150;}else{dx+=x;dy+=y;}}
      draw();
    });
    for(const event of ['pointerup','pointercancel','lostpointercapture'])canvas.addEventListener(event,e=>pointers.delete(e.pointerId));
    reset();
  }
})();
