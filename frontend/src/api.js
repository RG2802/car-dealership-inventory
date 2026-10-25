export async function request(path,{token,method='GET',body,signal}={}) {
 const response=await fetch('/api'+path,{method,signal,headers:{...(body?{'Content-Type':'application/json'}:{}),...(token?{Authorization:`Bearer ${token}`}:{})},...(body?{body:JSON.stringify(body)}:{})});
 if(response.status===204)return null;
 const data=await response.json();
 if(!response.ok){const detail=data.detail;const error=new Error(Array.isArray(detail)?detail.map(e=>`${e.loc.at(-1)}: ${e.msg}`).join('; '):detail||'Request failed');error.status=response.status;throw error;}
 return data;
}
