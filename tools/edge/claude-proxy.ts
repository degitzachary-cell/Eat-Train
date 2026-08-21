import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

/* The default is left where it was. Another app calls this function and
   changing the model underneath it would change its answers and its bill
   without anybody asking for that; callers that want something else say so. */
const DEFAULT_MODEL = "claude-3-5-haiku-20241022";

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }
  try {
    const { systemPrompt, userMsg, model, max_tokens, stream } = await req.json();

    const body = {
      model: model || DEFAULT_MODEL,
      max_tokens: max_tokens || 1000,
      system: systemPrompt,
      /* A string or an array of content blocks — an image block passes through
         here untouched, which is what lets a photograph of a label be read. */
      messages: [{ role: "user", content: userMsg }],
      ...(stream ? { stream: true } : {}),
    };

    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": Deno.env.get("ANTHROPIC_API_KEY") ?? "",
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify(body),
    });

    /* Streamed: hand the event stream straight back rather than waiting for
       the whole answer. The caller reads a field at a time as it arrives,
       which is the whole point of asking for it this way. */
    if (stream) {
      if (!res.ok) {
        const text = await res.text();
        return new Response(text, {
          status: res.status,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      return new Response(res.body, {
        headers: {
          ...corsHeaders,
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        },
      });
    }

    const data = await res.json();
    return new Response(JSON.stringify(data), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
