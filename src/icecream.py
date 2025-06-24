"""Defines ice cream properties."""

from pydantic import BaseModel, Field, ValidationError, field_validator


class IceCream(BaseModel):
    """Model template for Ice Cream."""

    Id: int = Field(gt=0, description="The Id must be an integer greater than zero")
    Name: str = Field(max_length=60)
    Price: float = Field(
        gt=0.0, description="The price must be a number greater than zero"
    )
    Quantity: int = Field(
        gt=0, description="The quantity must be an integer greater than zero"
    )
    OnDisplay: bool
    Description: str = Field(max_length=600)

    def __str__(self):
        return ",".join(
            [
                f"Id={self.Id}",
                f'Name="{self.Name}"',
                f"Cost={self.Price}",
                f"Quantity={self.Quantity}",
                f'Description="{self.Description}"',
            ]
        )

    def __eq__(self, other):
        if isinstance(other, type(self)) and (
            self is other
            or (
                self.Id == other.Id
                and self.Name == other.Name
                and self.Price == other.Price
                and self.Quantity == other.Quantity
                and self.Description == other.Description
            )
        ):
            return True

        return False

    def __hash__(self):
        return self.Id

    def tojson(self):
        """Performs the json conversion of the input ice cream object.

        :return: object in json format
        """
        jsonstr = "".join(
            [
                "{",
                f'"Id":{self.Id}, ',
                f'"Name":"{self.Name}", ',
                f'"Price":{self.Price}, ',
                f'"Description":"{self.Description}", ',
                f'"Quantity":{self.Quantity}',
                "}",
            ]
        )

        return jsonstr


if __name__ == "__main__":
    try:
        ic1 = IceCream(
            Id=2.1,
            Name="vanilla",
            Price=3.1,
            Quantity=100,
            Description="Vanilla Bean Ice Cream: Speck-tacular Flavor!",
        )
        print(ic1.tojson())
    except ValidationError as e:
        print(e)
