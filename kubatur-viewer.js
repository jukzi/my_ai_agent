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
  cases.triangleSigned={...triangleOutline,negativePoint:0,
    points:[[1/3,1/3],[3/5,1/5],[1/5,3/5],[1/5,1/5]]};
  cases.tetrahedronPositiveCubic={...cases.tetrahedron,
    points:[(1/12-shiftRoot)/2,(1/12+shiftRoot)/2].flatMap(t=>
      Array.from({length:4},(_,i)=>Array.from({length:3},(_,j)=>1/4+(i===j?3:-1)*t)))};
  cases.tetrahedronSigned={...cases.tetrahedron,negativePoint:0,points:[[.25,.25,.25],
    ...Array.from({length:4},(_,i)=>Array.from({length:3},(_,j)=>i===j?1/2:1/6))]};
  cases.tetrahedronCentroid={...cases.tetrahedron,points:[[.25,.25,.25]]};
  cases.cubeFaces={...cases.cube,points:[0,1,2].flatMap(axis=>[0,1].map(side=>[.5,.5,.5].map((v,i)=>i===axis?side:v)))};
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
      for(const [i,p] of scene.points.entries()){const [x,y]=project(p);ctx.beginPath();ctx.arc(x,y,scene.pointSize??7,0,2*Math.PI);ctx.fillStyle=i===scene.negativePoint?'#6941a5':'#d65b28';ctx.fill();ctx.strokeStyle='white';ctx.stroke();}
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
