from typing import Any

from asgiref.sync import sync_to_async

from usage.models import Charge, OpenAIModel, Organization


def store_charge(organization_id: str, response: Any) -> None:
    if not organization_id:
        return

    organization, _ = Organization.objects.get_or_create(
        openai_id=organization_id,
        defaults={
            'name': organization_id,
        },
    )
    model, _ = OpenAIModel.objects.get_or_create(name=response['model'],
                                                 defaults={'price_per_1k': 0})

    Charge.objects.create(
        organization=organization,
        tokens_used=response['usage']['total_tokens'],
        model=model,
    )


async def astore_charge(organization_id: str, response: Any) -> None:
    await sync_to_async(store_charge)(organization_id, response)
