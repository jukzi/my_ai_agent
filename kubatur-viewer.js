(() => {
  const cases = {
    square: {v:[[0,0],[1,0],[1,1],[0,1]], faces:[[0,1,2,3]], points:[-1,1].flatMap(i=>[-1,1].map(j=>[.5+i/(2*Math.sqrt(3)),.5+j/(2*Math.sqrt(3))]))},
    cube: {v:[[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]], faces:[[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]], points:[-1,1].flatMap(i=>[-1,1].flatMap(j=>[-1,1].map(k=>[i,j,k].map(x=>.5+x/(2*Math.sqrt(3))))))},
    triangle: {v:[[0,0],[1,0],[0,1]], faces:[[0,1,2]], points:[[1/6,1/6],[2/3,1/6],[1/6,2/3]]},
    tetrahedron: {v:[[0,0,0],[1,0,0],[0,1,0],[0,0,1]], faces:[[0,1,2],[0,1,3],[0,2,3],[1,2,3]], points:Array.from({length:4},(_,i)=>Array.from({length:3},(_,j)=>1/4+(i===j?3:-1)/(4*Math.sqrt(5))))}
  };
  for (const host of document.querySelectorAll('[data-kubatur-viewer]')) {
    const scene=cases[host.dataset.kubaturViewer]; if(!scene) continue;
    const spatial=scene.v[0].length===3;
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
      x-=spatial?.25:.5;y-=spatial?.25:.5;if(spatial)z-=.25;
      const X=x*Math.cos(a)-z*Math.sin(a), Z=x*Math.sin(a)+z*Math.cos(a);
      const Y=y*Math.cos(b)-Z*Math.sin(b);
      return [320+dx+220*zoom*X,210+dy-220*zoom*Y,y*Math.sin(b)+Z*Math.cos(b)];
    }
    function draw(){
      ctx.clearRect(0,0,640,420);
      const v=scene.v.map(project);
      const depth=f=>f.reduce((s,i)=>s+v[i][2],0)/f.length;
      for(const f of [...scene.faces].sort((l,r)=>depth(l)-depth(r))){
        ctx.beginPath(); f.forEach((i,j)=>j?ctx.lineTo(...v[i].slice(0,2)):ctx.moveTo(...v[i].slice(0,2)));ctx.closePath();ctx.fillStyle='#5eead445';ctx.fill();ctx.strokeStyle='#327c81';ctx.lineWidth=2;ctx.stroke();
      }
      for(const p of scene.points){const [x,y]=project(p);ctx.beginPath();ctx.arc(x,y,7,0,2*Math.PI);ctx.fillStyle='#d65b28';ctx.fill();ctx.strokeStyle='white';ctx.stroke();}
    }
    function magnify(f){zoom=Math.max(.3,Math.min(8,zoom*f));draw();}
    function button(label,icon,fn){const btn=document.createElement('button');btn.type='button';appearance(btn,label,icon);btn.addEventListener('click',fn);controls.append(btn);return btn;}
    button('Vergrößern','plus',()=>magnify(1.2));button('Verkleinern','minus',()=>magnify(1/1.2));button('Zurücksetzen','reset',reset);
    if(spatial){button('Links drehen','left',()=>{a-=.2;draw();});button('Rechts drehen','right',()=>{a+=.2;draw();});}
    if(host.requestFullscreen){const btn=button('Vollbild','full',async()=>{try{if(document.fullscreenElement===host)await document.exitFullscreen();else await host.requestFullscreen();}catch{appearance(btn,'Vollbild nicht verfügbar','full');}});document.addEventListener('fullscreenchange',()=>{const active=document.fullscreenElement===host;appearance(btn,active?'Vollbild verlassen':'Vollbild',active?'exit':'full');});}
    canvas.addEventListener('wheel',e=>{if(document.activeElement!==canvas)return;e.preventDefault();magnify(Math.exp(-Math.sign(e.deltaY)*.12));},{passive:false});
    canvas.addEventListener('keydown',e=>{const moves={ArrowLeft:[-15,0],ArrowRight:[15,0],ArrowUp:[0,-15],ArrowDown:[0,15]};if(moves[e.key]){const [x,y]=moves[e.key];dx+=x;dy+=y;draw();}else if(e.key==='+'||e.key==='=')magnify(1.2);else if(e.key==='-')magnify(1/1.2);else return;e.preventDefault();});
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
