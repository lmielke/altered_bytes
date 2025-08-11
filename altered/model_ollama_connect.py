# altered/ollama_connect.py  – REPLACE the previous version
from typing import Any, Dict, Callable, Optional
import json, httpx
from ollama import Client
from colorama import Fore

class OllamaConnect:
    """
    Direct bridge to the Ollama daemon.
    Signature preserved:  OllamaConnect()(ctx=ctx, url=url)
    """

    def __init__(self, *, url: str, timeout: int = 120, **__) -> None:
        self.url = url
        self.client = Client(host=self.url.split('/api', 1)[0], timeout=timeout)

    # ─── public entry ──────────────────────────────────────────────────────
    def __call__(self, *, ctx: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self._route(ctx)(ctx)
        except httpx.TimeoutException as err:
            return {"responses": [{"error": str(err)}]}

    # ─── routing helpers ───────────────────────────────────────────────────
    def _route(self, ctx: Dict[str, Any]) -> Callable:
        # print(f"\n\n\n{Fore.CYAN}_route with model:{Fore.RESET} \n{ctx}")
        if ctx.get("service_endpoint") == "embeddings":
            return self._embeddings
        if ctx.get("tools"):
            return self._chat
        return self._generate

    # ─── endpoints ────────────────────────────────────────────────────────
    def _generate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        # print(f"\n\n\n{Fore.RED}_generate with model:{Fore.RESET} \n{ctx}")
        rpt = ctx.get("repeats", {}).get("num", 1)
        outs = [self._once_generate(ctx) for _ in range(rpt)]
        return {"responses": outs, "num_results": len(outs)}

    def _once_generate(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        # print(f"\n\n\n{Fore.RED}_once_generate with model:{Fore.RESET} \n{ctx}")
        g = self.client.generate(model=ctx["model"],
                                 prompt="".join(ctx["prompts"]),
                                 options=ctx.get("options", {}),
                                 keep_alive=ctx.get("keep_alive", 200),
                                 stream=False)
        return {"response": g["response"], "tool_call": None}

    def _chat(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        # print(f"\n\n\n{Fore.RED}_chat with model:{Fore.RESET} \n{ctx}")
        messages = ctx.get("messages") or [{'role': 'user', 'content': p}
                                           for p in ctx.get("prompts", [])]
        tc_flag_none = ctx.get("tool_choice") == "none"
        tools = None if tc_flag_none else ctx.get("tools")
        msg = {}
        try:
            msg = self.client.chat(model=ctx["model"], messages=messages,
                               tools=tools,
                               keep_alive=ctx.get("keep_alive", 200),
                               stream=False)["message"]
        except Exception as e:
            msg['content'] = (
                                f"\n{Fore.RED}ERROR: model_ollama_connect._chat: "
                                f"\n{e}\n{self.url = }, {ctx['model'] =}{Fore.RESET}"
                                )
            print(msg['content'])
        tc = self._norm_tool((msg.get("tool_calls") or [None])[0])
        content = msg.get("content") or json.dumps({"tool_call": tc} )
        return {"responses": [{"response": content, "tool_call": tc}]}

    def _embeddings(self, ctx: Dict[str, Any]) -> Dict[str, Any]:
        vec = self.client.embeddings(model=ctx["model"],
                                     prompt="".join(ctx["prompts"]))
        return {"responses": [{"response": vec, "tool_call": None}]}

    # ─── misc helpers ──────────────────────────────────────────────────────
    @staticmethod
    def _norm_tool(tc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if tc is None:
            return None
        fn = tc["function"]
        return {"name": fn["name"], "arguments": fn["arguments"]}
