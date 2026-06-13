// Tactical combat — Gold Box style. Real party stats (CHRDATA) + decoded sprites (CBODY/CPIC).
// AD&D 1e-ish resolution: THAC0, AC, d20 to hit, weapon damage + STR bonus.
(function(global){
'use strict';
const GW=16, GH=11, CELL=30;           // tactical grid
function d(n){ return 1+Math.floor(Math.random()*n); }       // dN
function roll(n,s){ let t=0; for(let i=0;i<n;i++) t+=d(s); return t; }
function strHit(s){ return s>=18?1:(s>=17?1:(s>=16?0:(s<7?-1:0))); }
function strDmg(s,ex){ if(s>=18&&ex>=91)return 4; if(s>=18&&ex>=51)return 3; if(s>=18)return 2; if(s>=16)return 1; return 0; }

function classCombat(cls){
  switch(cls){
    case 'Fighter': return {thac0:20, ac:4, dmgDie:8,  hd:10, wname:'long sword'};
    case 'Cleric':  return {thac0:20, ac:5, dmgDie:6,  hd:8,  wname:'mace'};
    case 'Thief':   return {thac0:20, ac:7, dmgDie:6,  hd:6,  wname:'short sword'};
    case 'Magic-User': return {thac0:20, ac:9, dmgDie:4, hd:4, wname:'dagger'};
    default: return {thac0:20, ac:6, dmgDie:6, hd:8, wname:'weapon'};
  }
}
const MTYPES=[
  {name:'Kobold', ac:7, thac0:20, hd:1, dmg:6, mv:9},
  {name:'Orc',    ac:6, thac0:19, hd:1, dmg:8, mv:9},
  {name:'Goblin', ac:6, thac0:20, hd:1, dmg:6, mv:6},
  {name:'Hobgoblin', ac:5, thac0:19, hd:2, dmg:8, mv:9},
];

function Combat(ctx, data, onEnd){
  this.ctx=ctx; this.data=data; this.onEnd=onEnd;
  this.units=[]; this.msg=[]; this.over=false;
  // weapon damage dice (AD&D), keyed off the decoded .ITM weapon name
  const WPN=[[/two.?hand/i,10],[/long ?sword|broad ?sword|bastard/i,8],[/flail|mace|morning/i,8],
             [/short ?sword|scimitar/i,6],[/dagger/i,4],[/dart/i,3],[/sling|staff/i,6],[/spear|halberd/i,8]];
  function weaponOf(items){
    if(items) for(const it of items){ for(const[re,die] of WPN) if(re.test(it)) return {name:it,die:die}; }
    return null;
  }
  // party along left columns
  const sprites=data.combat;
  data.party.forEach((c,i)=>{
    const cc=classCombat(c.cls);
    const w=weaponOf(c.items);
    this.units.push({
      side:'pc', name:c.name, cls:c.cls,
      x:1+(i%2), y:2+i, mhp:Math.max(c.hp,1), hp:Math.max(c.hp,1),
      ac:cc.ac, thac0:cc.thac0, dmgDie:w?w.die:cc.dmgDie, wname:w?w.name:cc.wname,
      str:c.stats.STR, exstr:c.exstr||0, dex:c.stats.DEX, mv:6,
      sprite:sprites[i%sprites.length].url, w:sprites[0].w, h:sprites[0].h, dead:false
    });
  });
  // monsters along right columns — count scales, types from decoded CPIC
  const nm=3+Math.floor(Math.random()*4);
  const ms=data.monsters;
  for(let i=0;i<nm;i++){
    const t=MTYPES[i%MTYPES.length], spr=ms[(i*2)%ms.length];
    this.units.push({
      side:'mon', name:t.name+' '+(i+1), x:GW-2-(i%2), y:2+i,
      mhp:Math.max(roll(t.hd,8),1), ac:t.ac, thac0:t.thac0, dmgDie:t.dmg, mv:t.mv,
      sprite:spr.url, w:spr.w, h:spr.h, dead:false, str:12, exstr:0, dex:11, wname:'claw'
    });
    this.units[this.units.length-1].hp=this.units[this.units.length-1].mhp;
  }
  // initiative order: DEX desc
  this.order=this.units.map((u,i)=>i).sort((a,b)=>this.units[b].dex-this.units[a].dex);
  this.turn=0;
  this.log(`A wandering encounter! ${nm} foes block the passage.`);
  this.beginTurn();
}
Combat.prototype.log=function(m){ this.msg.push(m); if(this.msg.length>5)this.msg.shift(); };
Combat.prototype.cur=function(){ return this.units[this.order[this.turn]]; };
Combat.prototype.unitAt=function(x,y){ return this.units.find(u=>!u.dead&&u.x===x&&u.y===y); };
Combat.prototype.alive=function(side){ return this.units.filter(u=>!u.dead&&u.side===side); };

Combat.prototype.beginTurn=function(){
  if(this.over) return;
  if(!this.alive('mon').length){ this.finish(true); return; }
  if(!this.alive('pc').length){ this.finish(false); return; }
  let u=this.cur();
  let guard=0;
  while(u.dead && guard++<50){ this.turn=(this.turn+1)%this.order.length; u=this.cur(); }
  this.moved=0; this.acted=false;
  if(u.side==='mon'){ setTimeout(()=>this.monsterAI(u),420); }
  this.render();
};
Combat.prototype.endTurn=function(){
  this.turn=(this.turn+1)%this.order.length; this.beginTurn();
};
Combat.prototype.dist=function(a,b){ return Math.abs(a.x-b.x)+Math.abs(a.y-b.y); };

Combat.prototype.attack=function(att,def){
  const need=att.thac0 - (def.ac);     // d20 must be >= THAC0 - AC
  const r=d(20);
  const hitBonus = att.side==='pc'? strHit(att.str):0;
  if(r+hitBonus>=need || r===20){
    const dmg=Math.max(1, d(att.dmgDie)+(att.side==='pc'?strDmg(att.str,att.exstr):0));
    def.hp-=dmg;
    this.log(`${att.name} hits ${def.name} with ${att.wname} for ${dmg} (d20 ${r}${hitBonus?'+'+hitBonus:''} vs ${need}).`);
    if(def.hp<=0){ def.dead=true; this.log(`${def.name} falls!`); }
  } else {
    this.log(`${att.name} misses ${def.name} (d20 ${r}${hitBonus?'+'+hitBonus:''} vs ${need}).`);
  }
  this.acted=true;
};
Combat.prototype.monsterAI=function(u){
  if(this.over||u.dead) return;
  // find nearest pc
  const tgts=this.alive('pc'); if(!tgts.length){ this.finish(false); return; }
  tgts.sort((a,b)=>this.dist(u,a)-this.dist(u,b));
  const t=tgts[0];
  // step toward, up to mv (simplified: move along the bigger axis)
  let steps=Math.min(u.mv, this.dist(u,t)-1>=0?u.mv:0);
  while(steps-->0 && this.dist(u,t)>1){
    const dx=Math.sign(t.x-u.x), dy=Math.sign(t.y-u.y);
    let nx=u.x+(Math.abs(t.x-u.x)>=Math.abs(t.y-u.y)?dx:0);
    let ny=u.y+(Math.abs(t.x-u.x)>=Math.abs(t.y-u.y)?0:dy);
    if(nx<0||ny<0||nx>=GW||ny>=GH||this.unitAt(nx,ny)){ break; }
    u.x=nx; u.y=ny;
  }
  if(this.dist(u,t)<=1) this.attack(u,t);
  this.render();
  setTimeout(()=>{ if(!this.over) this.endTurn(); }, 360);
};

Combat.prototype.click=function(gx,gy){
  if(this.over) return;
  const u=this.cur(); if(u.side!=='pc') return;
  const tgt=this.unitAt(gx,gy);
  if(tgt && tgt.side==='mon' && this.dist(u,tgt)<=1 && !this.acted){
    this.attack(u,tgt); this.render();
    setTimeout(()=>this.endTurn(),250); return;
  }
  // move
  if(!tgt && this.dist(u,{x:gx,y:gy})<=u.mv-this.moved && gx>=0&&gy>=0&&gx<GW&&gy<GH){
    this.moved+=this.dist(u,{x:gx,y:gy}); u.x=gx; u.y=gy; this.render();
    // auto-attack if now adjacent to a foe
    const adj=this.alive('mon').find(m=>this.dist(u,m)<=1);
    if(adj && !this.acted){ this.log(`${u.name} closes on ${adj.name}.`); }
  }
};
Combat.prototype.pass=function(){ if(!this.over && this.cur().side==='pc'){ this.log(`${this.cur().name} holds.`); this.endTurn(); } };
// autoplay: one complete PC action (move toward nearest foe, attack if adjacent), then end turn
Combat.prototype.autoAct=function(){
  if(this.over) return;
  const u=this.cur(); if(!u || u.side!=='pc') return;
  const foes=this.alive('mon'); if(!foes.length) return;
  foes.sort((a,b)=>this.dist(u,a)-this.dist(u,b));
  const t=foes[0];
  if(this.dist(u,t)<=1){ this.attack(u,t); this.render(); setTimeout(()=>{ if(!this.over) this.endTurn(); },250); return; }
  // step toward target along the bigger axis, up to movement
  let steps=u.mv;
  while(steps-->0 && this.dist(u,t)>1){
    const dx=Math.sign(t.x-u.x), dy=Math.sign(t.y-u.y);
    let nx=u.x+(Math.abs(t.x-u.x)>=Math.abs(t.y-u.y)?dx:0);
    let ny=u.y+(Math.abs(t.x-u.x)>=Math.abs(t.y-u.y)?0:dy);
    if(nx<0||ny<0||nx>=GW||ny>=GH||this.unitAt(nx,ny)) break;
    u.x=nx; u.y=ny;
  }
  this.render();
  if(this.dist(u,t)<=1){ setTimeout(()=>{ this.attack(u,t); this.render(); setTimeout(()=>{ if(!this.over) this.endTurn(); },250); },250); }
  else setTimeout(()=>{ if(!this.over) this.endTurn(); },250);
};

Combat.prototype.finish=function(win){
  this.over=true;
  let treasure='';
  if(win && this.data.loot && this.data.loot.length){
    const n=1+Math.floor(Math.random()*3), picks=[];
    for(let i=0;i<n;i++) picks.push(this.data.loot[Math.floor(Math.random()*this.data.loot.length)]);
    treasure=' The bodies yield treasure: '+picks.join(', ')+'.';
  }
  this.log((win?'Victory! The foes are slain.':'The party has fallen...')+treasure);
  this.render();
  setTimeout(()=>this.onEnd&&this.onEnd(win, treasure), 1900);
};

Combat.prototype.render=function(){
  const cx=this.ctx, VW=cx.canvas.width, VH=cx.canvas.height;
  const ox=(VW-GW*CELL)/2, oy=8;
  cx.clearRect(0,0,VW,VH);
  cx.fillStyle='#0a0a10'; cx.fillRect(0,0,VW,VH);
  // grid
  cx.strokeStyle='#1c2030'; cx.lineWidth=1;
  for(let x=0;x<=GW;x++){ cx.beginPath();cx.moveTo(ox+x*CELL,oy);cx.lineTo(ox+x*CELL,oy+GH*CELL);cx.stroke(); }
  for(let y=0;y<=GH;y++){ cx.beginPath();cx.moveTo(ox,oy+y*CELL);cx.lineTo(ox+GW*CELL,oy+y*CELL);cx.stroke(); }
  const u=this.cur();
  // highlight current unit's reachable cells
  if(u && u.side==='pc' && !this.over){
    cx.fillStyle='rgba(80,140,90,0.18)';
    for(let y=0;y<GH;y++)for(let x=0;x<GW;x++){
      if(Math.abs(x-u.x)+Math.abs(y-u.y)<=u.mv-this.moved && !this.unitAt(x,y))
        cx.fillRect(ox+x*CELL+1,oy+y*CELL+1,CELL-1,CELL-1);
    }
    cx.strokeStyle='#fc4'; cx.lineWidth=2;
    cx.strokeRect(ox+u.x*CELL+1,oy+u.y*CELL+1,CELL-2,CELL-2);
  }
  // units
  this.units.forEach(un=>{
    if(un.dead) return;
    const px=ox+un.x*CELL, py=oy+un.y*CELL;
    if(!un._img){ un._img=new Image(); un._img.onload=()=>{ if(!this._rerender){ this._rerender=true; setTimeout(()=>{this._rerender=false; this.render();},30);} }; un._img.src=un.sprite; }
    cx.save();
    if(un.side==='mon'){ cx.translate(px+CELL,py); cx.scale(-1,1); cx.drawImage(un._img,0,0,CELL,CELL); }
    else cx.drawImage(un._img,px,py,CELL,CELL);
    cx.restore();
    // hp bar
    const f=Math.max(0,un.hp/un.mhp);
    cx.fillStyle='#300'; cx.fillRect(px+2,py+CELL-4,CELL-4,3);
    cx.fillStyle=un.side==='pc'?'#5d5':'#d55'; cx.fillRect(px+2,py+CELL-4,(CELL-4)*f,3);
  });
  // message log
  cx.fillStyle='#9c9'; cx.font='12px "Courier New"';
  this.msg.forEach((m,i)=> cx.fillText(m, 8, oy+GH*CELL+16+i*14));
  // turn banner
  cx.fillStyle='#fc4'; cx.font='bold 13px "Courier New"';
  cx.fillText(this.over?'— combat over —':`${u.name}'s turn  (${u.side==='pc'?'click green to move, click foe to attack, SPACE to hold':'enemy acting...'})`, 8, oy+GH*CELL+2);
};
Combat.GW=GW; Combat.GH=GH; Combat.CELL=CELL;
global.Combat=Combat;
})(window);
